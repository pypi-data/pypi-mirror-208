from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

import attr

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.project_version_in_git_dag import ProjectVersionInGitDag
    from ..models.project_version_in_git_tags import ProjectVersionInGitTags


T = TypeVar("T", bound="ProjectVersionInGit")


@attr.s(auto_attribs=True)
class ProjectVersionInGit:
    """
    Attributes:
        project_id (int): The ID of the project to create a version for
        name (str): The name of the project version
        git_repo (str): The git repo for the project version
        git_hash (str): The git hash for the project version
        committed (bool): Whether or not the project version has been committed
        dag (ProjectVersionInGitDag): The DAG for the project version
        dag_schema_version (int): The schema version of the DAG
        tags (Union[Unset, ProjectVersionInGitTags]): Tags for the project version
    """

    project_id: int
    name: str
    git_repo: str
    git_hash: str
    committed: bool
    dag: "ProjectVersionInGitDag"
    dag_schema_version: int
    tags: Union[Unset, "ProjectVersionInGitTags"] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        project_id = self.project_id
        name = self.name
        git_repo = self.git_repo
        git_hash = self.git_hash
        committed = self.committed
        dag = self.dag.to_dict()

        dag_schema_version = self.dag_schema_version
        tags: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.tags, Unset):
            tags = self.tags.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "project_id": project_id,
                "name": name,
                "git_repo": git_repo,
                "git_hash": git_hash,
                "committed": committed,
                "dag": dag,
                "dag_schema_version": dag_schema_version,
            }
        )
        if tags is not UNSET:
            field_dict["tags"] = tags

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.project_version_in_git_dag import ProjectVersionInGitDag
        from ..models.project_version_in_git_tags import ProjectVersionInGitTags

        d = src_dict.copy()
        project_id = d.pop("project_id")

        name = d.pop("name")

        git_repo = d.pop("git_repo")

        git_hash = d.pop("git_hash")

        committed = d.pop("committed")

        dag = ProjectVersionInGitDag.from_dict(d.pop("dag"))

        dag_schema_version = d.pop("dag_schema_version")

        _tags = d.pop("tags", UNSET)
        tags: Union[Unset, ProjectVersionInGitTags]
        if isinstance(_tags, Unset):
            tags = UNSET
        else:
            tags = ProjectVersionInGitTags.from_dict(_tags)

        project_version_in_git = cls(
            project_id=project_id,
            name=name,
            git_repo=git_repo,
            git_hash=git_hash,
            committed=committed,
            dag=dag,
            dag_schema_version=dag_schema_version,
            tags=tags,
        )

        project_version_in_git.additional_properties = d
        return project_version_in_git

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
