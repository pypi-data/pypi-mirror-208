import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union, cast

import attr
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.run_log_in_config import RunLogInConfig
    from ..models.run_log_in_inputs import RunLogInInputs
    from ..models.run_log_in_run_log import RunLogInRunLog
    from ..models.run_log_in_tags import RunLogInTags


T = TypeVar("T", bound="RunLogIn")


@attr.s(auto_attribs=True)
class RunLogIn:
    """
    Attributes:
        project_version_id (int): The ID of the project version to track with
        config (RunLogInConfig): The config with which the DAG was run
        run_id (str): User-generated run ID
        start_time (datetime.datetime): The time the run started
        end_time (datetime.datetime): The time the run ended
        run_log_schema_version (int): The schema version of the run log
        run_log (RunLogInRunLog):
        status (str): The status of the run
        tags (Union[Unset, RunLogInTags]): Tags for the run
        inputs (Union[Unset, RunLogInInputs]): Inputs for the run
        outputs (Union[Unset, List[str]]): Outputs for the run
    """

    project_version_id: int
    config: "RunLogInConfig"
    run_id: str
    start_time: datetime.datetime
    end_time: datetime.datetime
    run_log_schema_version: int
    run_log: "RunLogInRunLog"
    status: str
    tags: Union[Unset, "RunLogInTags"] = UNSET
    inputs: Union[Unset, "RunLogInInputs"] = UNSET
    outputs: Union[Unset, List[str]] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        project_version_id = self.project_version_id
        config = self.config.to_dict()

        run_id = self.run_id
        start_time = self.start_time.isoformat()

        end_time = self.end_time.isoformat()

        run_log_schema_version = self.run_log_schema_version
        run_log = self.run_log.to_dict()

        status = self.status
        tags: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.tags, Unset):
            tags = self.tags.to_dict()

        inputs: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.inputs, Unset):
            inputs = self.inputs.to_dict()

        outputs: Union[Unset, List[str]] = UNSET
        if not isinstance(self.outputs, Unset):
            outputs = self.outputs

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "project_version_id": project_version_id,
                "config": config,
                "run_id": run_id,
                "start_time": start_time,
                "end_time": end_time,
                "run_log_schema_version": run_log_schema_version,
                "run_log": run_log,
                "status": status,
            }
        )
        if tags is not UNSET:
            field_dict["tags"] = tags
        if inputs is not UNSET:
            field_dict["inputs"] = inputs
        if outputs is not UNSET:
            field_dict["outputs"] = outputs

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.run_log_in_config import RunLogInConfig
        from ..models.run_log_in_inputs import RunLogInInputs
        from ..models.run_log_in_run_log import RunLogInRunLog
        from ..models.run_log_in_tags import RunLogInTags

        d = src_dict.copy()
        project_version_id = d.pop("project_version_id")

        config = RunLogInConfig.from_dict(d.pop("config"))

        run_id = d.pop("run_id")

        start_time = isoparse(d.pop("start_time"))

        end_time = isoparse(d.pop("end_time"))

        run_log_schema_version = d.pop("run_log_schema_version")

        run_log = RunLogInRunLog.from_dict(d.pop("run_log"))

        status = d.pop("status")

        _tags = d.pop("tags", UNSET)
        tags: Union[Unset, RunLogInTags]
        if isinstance(_tags, Unset):
            tags = UNSET
        else:
            tags = RunLogInTags.from_dict(_tags)

        _inputs = d.pop("inputs", UNSET)
        inputs: Union[Unset, RunLogInInputs]
        if isinstance(_inputs, Unset):
            inputs = UNSET
        else:
            inputs = RunLogInInputs.from_dict(_inputs)

        outputs = cast(List[str], d.pop("outputs", UNSET))

        run_log_in = cls(
            project_version_id=project_version_id,
            config=config,
            run_id=run_id,
            start_time=start_time,
            end_time=end_time,
            run_log_schema_version=run_log_schema_version,
            run_log=run_log,
            status=status,
            tags=tags,
            inputs=inputs,
            outputs=outputs,
        )

        run_log_in.additional_properties = d
        return run_log_in

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
