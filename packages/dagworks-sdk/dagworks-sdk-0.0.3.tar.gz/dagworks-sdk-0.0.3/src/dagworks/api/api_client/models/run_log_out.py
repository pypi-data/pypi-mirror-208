import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union, cast

import attr
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.run_log_out_config import RunLogOutConfig
    from ..models.run_log_out_inputs import RunLogOutInputs
    from ..models.run_log_out_tags import RunLogOutTags


T = TypeVar("T", bound="RunLogOut")


@attr.s(auto_attribs=True)
class RunLogOut:
    """
    Attributes:
        project_version (int):
        config (RunLogOutConfig):
        run_id (str):
        start_time (datetime.datetime):
        end_time (datetime.datetime):
        run_log_pointer (str):
        run_log_schema_version (int):
        created_at (datetime.datetime):
        updated_at (datetime.datetime):
        status (str):
        username_resolved (str):
        id (Union[Unset, int]):
        inputs (Union[Unset, RunLogOutInputs]):
        outputs (Union[Unset, List[Any]]):
        tags (Union[Unset, RunLogOutTags]):
        username (Union[Unset, int]):
        slug (Union[Unset, str]):
    """

    project_version: int
    config: "RunLogOutConfig"
    run_id: str
    start_time: datetime.datetime
    end_time: datetime.datetime
    run_log_pointer: str
    run_log_schema_version: int
    created_at: datetime.datetime
    updated_at: datetime.datetime
    status: str
    username_resolved: str
    id: Union[Unset, int] = UNSET
    inputs: Union[Unset, "RunLogOutInputs"] = UNSET
    outputs: Union[Unset, List[Any]] = UNSET
    tags: Union[Unset, "RunLogOutTags"] = UNSET
    username: Union[Unset, int] = UNSET
    slug: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        project_version = self.project_version
        config = self.config.to_dict()

        run_id = self.run_id
        start_time = self.start_time.isoformat()

        end_time = self.end_time.isoformat()

        run_log_pointer = self.run_log_pointer
        run_log_schema_version = self.run_log_schema_version
        created_at = self.created_at.isoformat()

        updated_at = self.updated_at.isoformat()

        status = self.status
        username_resolved = self.username_resolved
        id = self.id
        inputs: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.inputs, Unset):
            inputs = self.inputs.to_dict()

        outputs: Union[Unset, List[Any]] = UNSET
        if not isinstance(self.outputs, Unset):
            outputs = self.outputs

        tags: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.tags, Unset):
            tags = self.tags.to_dict()

        username = self.username
        slug = self.slug

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "project_version": project_version,
                "config": config,
                "run_id": run_id,
                "start_time": start_time,
                "end_time": end_time,
                "run_log_pointer": run_log_pointer,
                "run_log_schema_version": run_log_schema_version,
                "created_at": created_at,
                "updated_at": updated_at,
                "status": status,
                "username_resolved": username_resolved,
            }
        )
        if id is not UNSET:
            field_dict["id"] = id
        if inputs is not UNSET:
            field_dict["inputs"] = inputs
        if outputs is not UNSET:
            field_dict["outputs"] = outputs
        if tags is not UNSET:
            field_dict["tags"] = tags
        if username is not UNSET:
            field_dict["username"] = username
        if slug is not UNSET:
            field_dict["slug"] = slug

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.run_log_out_config import RunLogOutConfig
        from ..models.run_log_out_inputs import RunLogOutInputs
        from ..models.run_log_out_tags import RunLogOutTags

        d = src_dict.copy()
        project_version = d.pop("project_version")

        config = RunLogOutConfig.from_dict(d.pop("config"))

        run_id = d.pop("run_id")

        start_time = isoparse(d.pop("start_time"))

        end_time = isoparse(d.pop("end_time"))

        run_log_pointer = d.pop("run_log_pointer")

        run_log_schema_version = d.pop("run_log_schema_version")

        created_at = isoparse(d.pop("created_at"))

        updated_at = isoparse(d.pop("updated_at"))

        status = d.pop("status")

        username_resolved = d.pop("username_resolved")

        id = d.pop("id", UNSET)

        _inputs = d.pop("inputs", UNSET)
        inputs: Union[Unset, RunLogOutInputs]
        if isinstance(_inputs, Unset):
            inputs = UNSET
        else:
            inputs = RunLogOutInputs.from_dict(_inputs)

        outputs = cast(List[Any], d.pop("outputs", UNSET))

        _tags = d.pop("tags", UNSET)
        tags: Union[Unset, RunLogOutTags]
        if isinstance(_tags, Unset):
            tags = UNSET
        else:
            tags = RunLogOutTags.from_dict(_tags)

        username = d.pop("username", UNSET)

        slug = d.pop("slug", UNSET)

        run_log_out = cls(
            project_version=project_version,
            config=config,
            run_id=run_id,
            start_time=start_time,
            end_time=end_time,
            run_log_pointer=run_log_pointer,
            run_log_schema_version=run_log_schema_version,
            created_at=created_at,
            updated_at=updated_at,
            status=status,
            username_resolved=username_resolved,
            id=id,
            inputs=inputs,
            outputs=outputs,
            tags=tags,
            username=username,
            slug=slug,
        )

        run_log_out.additional_properties = d
        return run_log_out

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
