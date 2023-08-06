import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

import attr
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.hamilton_dag import HamiltonDAG
    from ..models.project_version_out_with_dag_tags import ProjectVersionOutWithDAGTags
    from ..models.project_version_out_with_dag_version_info import (
        ProjectVersionOutWithDAGVersionInfo,
    )


T = TypeVar("T", bound="ProjectVersionOutWithDAG")


@attr.s(auto_attribs=True)
class ProjectVersionOutWithDAG:
    """
    Attributes:
        project (int):
        name (str):
        version_info (ProjectVersionOutWithDAGVersionInfo):
        version_info_type (str):
        version_info_schema (int):
        dag_pointer (str):
        dag_schema_version (int):
        created_at (datetime.datetime):
        updated_at (datetime.datetime):
        logged_by (int):
        dag (HamiltonDAG): Represents a logical DAG
        id (Union[Unset, int]):
        slug (Union[Unset, str]):
        tags (Union[Unset, ProjectVersionOutWithDAGTags]):
        active (Union[Unset, bool]):  Default: True.
    """

    project: int
    name: str
    version_info: "ProjectVersionOutWithDAGVersionInfo"
    version_info_type: str
    version_info_schema: int
    dag_pointer: str
    dag_schema_version: int
    created_at: datetime.datetime
    updated_at: datetime.datetime
    logged_by: int
    dag: "HamiltonDAG"
    id: Union[Unset, int] = UNSET
    slug: Union[Unset, str] = UNSET
    tags: Union[Unset, "ProjectVersionOutWithDAGTags"] = UNSET
    active: Union[Unset, bool] = True
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        project = self.project
        name = self.name
        version_info = self.version_info.to_dict()

        version_info_type = self.version_info_type
        version_info_schema = self.version_info_schema
        dag_pointer = self.dag_pointer
        dag_schema_version = self.dag_schema_version
        created_at = self.created_at.isoformat()

        updated_at = self.updated_at.isoformat()

        logged_by = self.logged_by
        dag = self.dag.to_dict()

        id = self.id
        slug = self.slug
        tags: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.tags, Unset):
            tags = self.tags.to_dict()

        active = self.active

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "project": project,
                "name": name,
                "version_info": version_info,
                "version_info_type": version_info_type,
                "version_info_schema": version_info_schema,
                "dag_pointer": dag_pointer,
                "dag_schema_version": dag_schema_version,
                "created_at": created_at,
                "updated_at": updated_at,
                "logged_by": logged_by,
                "dag": dag,
            }
        )
        if id is not UNSET:
            field_dict["id"] = id
        if slug is not UNSET:
            field_dict["slug"] = slug
        if tags is not UNSET:
            field_dict["tags"] = tags
        if active is not UNSET:
            field_dict["active"] = active

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.hamilton_dag import HamiltonDAG
        from ..models.project_version_out_with_dag_tags import ProjectVersionOutWithDAGTags
        from ..models.project_version_out_with_dag_version_info import (
            ProjectVersionOutWithDAGVersionInfo,
        )

        d = src_dict.copy()
        project = d.pop("project")

        name = d.pop("name")

        version_info = ProjectVersionOutWithDAGVersionInfo.from_dict(d.pop("version_info"))

        version_info_type = d.pop("version_info_type")

        version_info_schema = d.pop("version_info_schema")

        dag_pointer = d.pop("dag_pointer")

        dag_schema_version = d.pop("dag_schema_version")

        created_at = isoparse(d.pop("created_at"))

        updated_at = isoparse(d.pop("updated_at"))

        logged_by = d.pop("logged_by")

        dag = HamiltonDAG.from_dict(d.pop("dag"))

        id = d.pop("id", UNSET)

        slug = d.pop("slug", UNSET)

        _tags = d.pop("tags", UNSET)
        tags: Union[Unset, ProjectVersionOutWithDAGTags]
        if isinstance(_tags, Unset):
            tags = UNSET
        else:
            tags = ProjectVersionOutWithDAGTags.from_dict(_tags)

        active = d.pop("active", UNSET)

        project_version_out_with_dag = cls(
            project=project,
            name=name,
            version_info=version_info,
            version_info_type=version_info_type,
            version_info_schema=version_info_schema,
            dag_pointer=dag_pointer,
            dag_schema_version=dag_schema_version,
            created_at=created_at,
            updated_at=updated_at,
            logged_by=logged_by,
            dag=dag,
            id=id,
            slug=slug,
            tags=tags,
            active=active,
        )

        project_version_out_with_dag.additional_properties = d
        return project_version_out_with_dag

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
