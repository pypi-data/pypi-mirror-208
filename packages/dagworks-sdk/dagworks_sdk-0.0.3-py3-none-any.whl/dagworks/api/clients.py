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

import abc
import dataclasses
import logging
from typing import Any, Dict, List

from dagworks.api.api_client import AuthenticatedClient
from dagworks.api.api_client.api.auth import trackingserver_api_api_phone_home as phone_home
from dagworks.api.api_client.api.projects import (
    trackingserver_api_api_create_project_version as create_project_version,
)
from dagworks.api.api_client.api.projects import (
    trackingserver_api_api_get_project_by_id as get_project_by_id,
)
from dagworks.api.api_client.api.projects import (
    trackingserver_api_api_get_project_versions as get_project_versions,
)
from dagworks.api.api_client.api.runs import trackingserver_api_api_log_run as log_run_log
from dagworks.api.api_client.models import (
    ProjectOut,
    ProjectVersionInGit,
    ProjectVersionInGitDag,
    ProjectVersionInGitTags,
    ProjectVersionOut,
    RunLogIn,
    RunLogInConfig,
    RunLogInRunLog,
    RunLogInTags,
    RunLogInInputs,
)
from dagworks.api.projecttypes import GitInfo
from dagworks.parsing.dagtypes import LogicalDAG
from dagworks.telemetry.telemetry import global_tracker
from dagworks.tracking.trackingtypes import DAGRun

logger = logging.getLogger(__name__)


class DAGWorksClient:
    def __init__(self, api_key: str, username: str, dw_api_url: str):
        """Initializes a DAGWorks client

         project: Project to save to
        :param api_key: API key to save to
        :param username: Username to authenticate against
        :param dw_api_url: API URL for DAGWorks API.
        """
        self.api_key = api_key
        self.username = username
        self.dw_api_url = dw_api_url

    @abc.abstractmethod
    def validate_auth(self):
        """Validates that authentication works against the DW API.
        Quick "phone-home" to ensure that everything is good to go."""
        pass

    @abc.abstractmethod
    def ensure_project_exists(self, project_id: int) -> ProjectOut:
        """Ensures that a project exists. If not, we create it.

        :param project_id: Project to ensure
        :return: True if the project exists, False if it was created.
        """
        pass

    @abc.abstractmethod
    def register_project_version(
        self, project_id: int, vcs_info: GitInfo, dag: LogicalDAG, name: str, tags: Dict[str, Any]
    ) -> ProjectVersionOut:
        """Registers a project version with the DAGWorks API.

        :param dag: DAG to save with this
        :param project_id: Project to register version for
        :param vcs_info: VCS info to register
        :param name: Name of the version to save the project with
        :return: Version ID -- likely commit hash for the project
        """
        pass

    @abc.abstractmethod
    def log_dag_run(
        self,
        dag_run: DAGRun,
        project_version_id: int,
        config: Dict[str, Any],
        tags: Dict[str, str],
        inputs: Dict[str, Any],
        outputs: List[str],
    ):
        """Logs a DAG run to the DAGWorks API.

        :param project_version_id:
        :param dag_run: DAG run to log
        :param config: config used to create DAG
        :param tags: Tags to log with the DAG run
        :param inputs: Inputs used to pass into the DAG
        :param outputs: Outputs used to query the DAG
        """
        pass


class BasicDAGWorksClient(DAGWorksClient):
    """Basic no-op DAGWorks client -- mocks out the above DAGWorks client for testing"""

    def __init__(self, api_key: str, username: str, dw_api_url: str):
        super().__init__(api_key, username, dw_api_url)
        self.api_client = AuthenticatedClient(
            dw_api_url,
            token=self.api_key,
            prefix="",
            auth_header_name="x-api-key",
            timeout=20.0,
            verify_ssl=True,
            raise_on_unexpected_status=True,
            headers={"x-api-user": f"{username}"},
        )

    @global_tracker.track_calls(params_to_capture_raw=["project_id"])
    def register_project_version(
        self,
        project_id: int,
        vcs_info: GitInfo,
        dag: LogicalDAG,
        name: str = None,
        tags: Dict[str, str] = None,
    ) -> ProjectVersionOut:
        if tags is None:
            tags = {}
        if name is None:
            # For backwards compatibility
            # People should add names to their versions
            name = vcs_info.commit_hash
        versions = get_project_versions.sync(
            client=self.api_client,
            project_id=project_id,
            git_hash=vcs_info.commit_hash,
            git_repo=vcs_info.repository,
            name=name,
        )
        if len(versions) > 0:
            logger.info(
                f"Version {vcs_info.commit_hash} with name: {name} already exists for project {project_id}. "
                f"Not saving the parsed DAG."
            )
            # TODO -- decide if we should update it? Store it? Do something else?
            # This should really be constant though -- I think the trick is
            # figuring out what to do with uncommitted code.
            # Otherwise if the parsed DAG changes its a bug/something at a system-level
            return versions[0]
        dag_to_save = ProjectVersionInGitDag()
        dag_to_save.additional_properties = dataclasses.asdict(dag)
        tags_to_save = ProjectVersionInGitTags()
        tags_to_save.additional_properties = tags
        return create_project_version.sync(
            client=self.api_client,
            json_body=ProjectVersionInGit(
                project_id=project_id,
                name=name,
                git_hash=vcs_info.commit_hash,
                git_repo=vcs_info.repository,
                committed=vcs_info.committed,
                dag=dag_to_save,
                dag_schema_version=dag.schema_version,
                tags=tags_to_save,
            ),
        )

    @global_tracker.track_calls()
    def validate_auth(self):
        """Validates that authentication works against the DW API."""
        result = phone_home.sync(client=self.api_client)
        if not result.success:
            raise ValueError(
                f"Auth for DAGWorks is not properly configured. "
                f"Received error: {result.message}."
            )

    @global_tracker.track_calls(params_to_capture_raw=["project"])
    def ensure_project_exists(self, project_id: int) -> ProjectOut:
        """Ensures that a project exists. If not, we create it."""
        # This is really ugly -- the code-generator doesn't allow nulls,
        # so we need to figure out the best way to signify that there *is* no project
        # TODO -- get the code-generator to allow nulls/fix the openapi spec we generate...
        # OR just add an endpoint to see if it already exists. An extra call won't hurt.
        # And then we can bypass it.
        project = get_project_by_id.sync(client=self.api_client, project_id=project_id)
        if project is None:
            raise ValueError(
                f"Project {project_id} does not exist. Perhaps you don't have access to "
                f"it (request write access from the creator), or perhaps you haven't made it yet..."
            )
        logger.debug(f"Project {project} already exists. Using project: {project}")
        return project

    @global_tracker.track_calls(params_to_capture_raw=["project_version_id"])
    def log_dag_run(
        self,
        dag_run: DAGRun,
        project_version_id: int,
        config: Dict[str, Any],
        tags: Dict[str, str],
        inputs: Dict[str, Any],
        outputs: List[str],
    ):
        run_log_to_save = RunLogInRunLog()
        run_log_to_save.additional_properties = {
            "tasks": [task.to_dict() for task in dag_run.tasks]
        }
        config_to_save = RunLogInConfig()
        config_to_save.additional_properties = config
        run_log_in_tags = RunLogInTags()
        run_log_in_tags.additional_properties = tags
        inputs_to_save = RunLogInInputs()
        inputs_to_save.additional_properties = inputs
        json_body = RunLogIn(
            status=dag_run.status.value,
            project_version_id=project_version_id,
            config=config_to_save,
            run_id=dag_run.run_id,
            start_time=dag_run.start_time,
            end_time=dag_run.end_time,
            run_log_schema_version=dag_run.schema_version,
            run_log=run_log_to_save,
            tags=run_log_in_tags,
            inputs=inputs_to_save,
            outputs=outputs,
        )
        log_run_log.sync(
            client=self.api_client,
            project_version_id=project_version_id,
            json_body=json_body,
        )
