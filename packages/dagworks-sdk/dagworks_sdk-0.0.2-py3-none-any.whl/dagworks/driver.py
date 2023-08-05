# Copyright (C) 2023-Present DAGWorks Inc.
#
# For full terms email support@dagworks.io.
#
# This software and associated documentation files (the "Software") may only be
# used in production, if you (and any entity that you represent) have agreed to,
# and are in compliance with, the DAGWorks Enterprise Terms of Service, available
# via email (support@dagworks.io) (the "Enterprise Terms"), or other
# agreement governing the use of the Software, as agreed by you and DAGWorks,
# and otherwise have a valid DAGWorks Enterprise license for the
# correct number of seats and usage volume.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import hashlib
import inspect
import json
import logging
import os
import uuid
from types import ModuleType
from typing import Any, Callable, Dict, List, Set, Tuple, Union

import git
from hamilton import base, driver

from dagworks.api import clients, constants
from dagworks.api.projecttypes import GitInfo
from dagworks.parsing.parse import parse_dag
from dagworks.telemetry.telemetry import get_adapter_representation, global_tracker
from dagworks.tracking.runs import Status, TrackingState, monkey_patch_adapter

logger = logging.getLogger(__name__)


def _hash_module(
    module: ModuleType, hash_object: hashlib.sha256, seen_modules: Set[ModuleType]
) -> hashlib.sha256:
    """Generate a hash of the specified module and its imports.

    It will recursively hash the contents of the modules and their imports, and only does so
    if the import is from the same package. This is to avoid hashing the entire python
    environment...

    :param module: the python module to hash and then crawl.
    :param hash_object: the object to update.
    :param seen_modules: the python modules we've already hashed.
    :return: the updated hash object
    """
    # Check if we've already hashed this module
    if module in seen_modules:
        return hash_object
    else:
        seen_modules.add(module)
    # Update the hash with the module's source code
    if hasattr(module, "__file__"):
        with open(module.__file__, "rb") as f:
            hash_object.update(f.read())
    else:
        logger.warning("Skipping hash for module %s because it has no __file__ attribute.", module)

    # Loop through the module's attributes
    for name, value in inspect.getmembers(module):
        # Check if the attribute is a module
        if inspect.ismodule(value):
            # Check if the module is in the same top level package
            if value.__package__ != module.__package__ and not value.__package__.startswith(
                module.__package__
            ):
                logger.debug(
                    f"Skipping hash for module {value.__name__} because it is in a different "
                    f"package {value.__package__} than {module.__package__}"
                )
                continue
            # Recursively hash the sub-module
            hash_object = _hash_module(value, hash_object, seen_modules)

    # Return the hash object
    return hash_object


def _get_modules_hash(modules: Tuple[ModuleType]) -> str:
    """Generate a hash of the contents of the specified modules.

    It recursively hashes the contents of the modules and their imports, and only does so
    if the import is from the same package. This is to avoid hashing the entire python
    environment...

    :param modules: python modules to hash
    :return: the hex digest of the hash
    """
    # Create a hash object
    h = hashlib.sha256()
    seen_modules = set()

    # Loop through each module name
    for module in modules:
        # Update the hash with the module's source code
        h = _hash_module(module, h, seen_modules)

    # Return the hex digest of the hash
    return h.hexdigest()


def _derive_version_control_info(module_hash: str) -> GitInfo:
    """Derive the git info for the current project.
    Currently, this decides whether we're in a git repository.
    This is not going to work for everything, but we'll see what the customers want.
    We might end up having to pass this data in...
    """
    try:
        repo = git.Repo(".", search_parent_directories=True)
    except git.exc.InvalidGitRepositoryError:
        logger.warning(
            "Warning: We are not currently in a git repository. We recommend using that as a "
            "way to version the "
            "project *if* your hamilton code lives within this repository too. If it does not,"
            " then we'll try to "
            "version code based on the python modules passed to the Driver. "
            "Incase you want to get set up with git quickly you can run:\n "
            "git init && git add . && git commit -m 'Initial commit'\n"
            "Still have questions? Reach out to stefan @ dagworks.io, elijah @ dagworks.io "
            "and we'll try to help you as soon as possible."
        )
        return GitInfo(
            branch="unknown",
            commit_hash=module_hash,
            committed=False,
            repository="Error: No repository to link to.",
            local_repo_base_path=os.getcwd(),
        )

    commit = repo.head.commit
    try:
        repo_url = repo.remote().url
    except ValueError:
        # TODO: change this to point to our docs on what to do.
        repo_url = "Error: No repository to link to."
    return GitInfo(
        branch=repo.active_branch.name,
        commit_hash=commit.hexsha,
        committed=not repo.is_dirty(),
        repository=repo_url,
        local_repo_base_path=repo.working_dir,
    )


def filter_config_to_json_serializable(config: Dict[str, Any], curr_result: Dict[str, Any] = None):
    if curr_result is None:
        curr_result = {}
    for key, value in config.items():
        try:
            json.dumps(value)
            curr_result[key] = value
        except TypeError:
            if isinstance(value, dict):
                new_result = {}
                filter_config_to_json_serializable(value, new_result)
                curr_result[key] = new_result
            else:
                curr_result[key] = str(value)
    return curr_result


def validate_tags(tags: Any):
    """Validates that tags are a dictionary of strings to strings.

    :param tags: Tags to validate
    :raises ValueError: If tags are not a dictionary of strings to strings
    """
    if not isinstance(tags, dict):
        raise ValueError(f"Tags must be a dictionary, but got {tags}")
    for key, value in tags.items():
        if not isinstance(key, str):
            raise ValueError(f"Tag keys must be strings, but got {key}")
        if not isinstance(value, str):
            raise ValueError(f"Tag values must be strings, but got {value}")


def safe_len(x):
    return len(x) if x is not None else 0


class Driver(driver.Driver):
    def __init__(
        self,
        config: Dict[str, Any],
        *modules: ModuleType,
        project_id: int,
        api_key: str,
        username: str,
        dag_name: str,
        tags: Dict[str, str] = None,
        client_factory: Callable[
            [str, str, str], clients.DAGWorksClient
        ] = clients.BasicDAGWorksClient,
        adapter: base.HamiltonGraphAdapter = None,
        dagworks_api_url=os.environ.get("DAGWORKS_API_URL", constants.DAGWORKS_API_URL),
    ):
        """Instantiates a DAGWorks driver. This:
        1. Requires a project to exist. Create one via https://app.dagworks.io/dashboard/projects.
        2. Sends over the shape of the DAG.
        3. Sets up execute() run-tracking.

        :param config: Configuration to use, same as standard Hamilton driver.
        :param modules: Modules to use, same as standard Hamilton driver.
        :param project_id: Identifier for the project to use to store this DAG under.
        :param api_key: API key to use for authentication. Remember not to save this in plaintext!
        :param username: email address to use for authentication.
        :param dag_name: name for this DAG. You will use this for top level curation of DAGs
        within a project.
        :param tags: Optional key value string pairs to help identify and curate this instance of
        the DAG and subsequent execution runs. E.g. {"environment": "production"}.
        Currently all .execute() runs will be tagged with these.
        :param client_factory: Optional. Advanced use. Factory to use to create the underlying
        client.
        :param adapter: Optional. Adapter to use, same as standard Hamilton driver.
        :param dagworks_api_url: Optional. URL to use for the DAGWorks API.
        """
        super(Driver, self).__init__(config, *modules, adapter=adapter)
        if global_tracker.enabled:
            global_tracker.initialize(
                username,
                project=project_id,
                adapter=get_adapter_representation(self.adapter),
                dagworks_api_url=dagworks_api_url,
            )
        self.config = config
        self.project = project_id
        self.api_key = api_key
        self.username = username
        # TODO -- figure out how to pass any additional configuration to the client if needed
        self.client = client_factory(api_key, username, dagworks_api_url)
        self.module_hash = _get_modules_hash(modules)
        self.vcs_info = _derive_version_control_info(self.module_hash)
        self.initialized = False
        self.modules = modules
        self.project_version = None
        self.run_tags = tags if tags is not None else {}
        validate_tags(self.run_tags)
        self.dag_name = dag_name

    @global_tracker.track_calls()
    def initialize(self):
        """Initializes the driver. This:
        1. Validates authentication
        2. Creates a project if it does not already exist
        3. Sets initialization as true

        Note this is idempotent -- it can be called by the user to test, but will get called when
        the driver runs.

        """
        logger.debug("Validating authentication against DAGWorks API...")
        self.client.validate_auth()
        logger.debug("Authentication successful!")
        logger.debug(f"Ensuring project {self.project} exists...")
        project_queried = self.client.ensure_project_exists(self.project)
        logger.debug("Inspecting DAG to save to DAGWorks...")
        # We pass in the config as we need to understand the shape of the DAG
        # TODO -- add the notion of multiple variants of a DAG version that we can "superimpose"
        dag = parse_dag(
            *self.modules, repo_base=self.vcs_info.local_repo_base_path, config=self.config
        )
        logger.debug(f"Found a total of {len(dag.nodes)} nodes in DAG, saving...")
        project_version = self.client.register_project_version(
            project_queried.id, self.vcs_info, dag=dag, name=self.dag_name, tags=self.run_tags
        )
        self.project_version = project_version
        logger.debug("Successfully saved DAG to DAGWorks...")
        self.initialized = True

    @global_tracker.track_calls(
        tracking_generators={
            "final_vars": [("num_vars", safe_len)],
            "overrides": [("num_overrides", safe_len)],
            "inputs": [("num_inputs", safe_len)],
        },
    )
    def execute(
        self,
        final_vars: List[Union[str, Callable]],
        overrides: Dict[str, Any] = None,
        display_graph: bool = False,
        inputs: Dict[str, Any] = None,
    ) -> Any:
        logger.warning(
            f"\nCapturing execution run. Results can be found at "
            f"https://app.dagworks.io/dashboard/project/{self.project}/runs\n"
        )
        return super(Driver, self).execute(final_vars, overrides, display_graph, inputs)

    @global_tracker.track_calls(
        tracking_generators={
            "final_vars": [("num_vars", safe_len)],
            "overrides": [("num_overrides", safe_len)],
            "inputs": [("num_inputs", safe_len)],
        },
    )
    def raw_execute(
        self,
        final_vars: List[Union[str, Callable]],
        overrides: Dict[str, Any] = None,
        display_graph: bool = False,
        inputs: Dict[str, Any] = None,
    ) -> Any:
        """Executes the DAG -- we decorate raw_execute, as execute delegates to raw_execute
        and we don't want to run twice. We should change this later, but for now this is OK.

        :param final_vars: Final variables to run
        :param overrides:
        :param display_graph:
        :param inputs:
        :return:
        """
        run_id = str(uuid.uuid4())
        tracking_state = TrackingState(str(run_id))
        with monkey_patch_adapter(self.adapter, tracking_state):
            if not self.initialized:
                self.initialize()
            tracking_state.clock_start()
            try:
                out = super(Driver, self).raw_execute(
                    final_vars=final_vars,
                    overrides=overrides,
                    display_graph=display_graph,
                    inputs=inputs,
                )
                tracking_state.clock_end(status=Status.SUCCESS)
                return out
            except Exception as e:
                tracking_state.clock_end(status=Status.FAILURE)
                raise e
            finally:
                self.client.log_dag_run(
                    tracking_state.get(),
                    self.project_version.id,
                    config=filter_config_to_json_serializable(self.config),
                    tags=self.run_tags,
                )
