from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar

import attr

if TYPE_CHECKING:
    from ..models.project_in_tags import ProjectInTags


T = TypeVar("T", bound="ProjectIn")


@attr.s(auto_attribs=True)
class ProjectIn:
    """
    Attributes:
        name (str): The name of the project
        description (str): Description of the project
        tags (ProjectInTags): Tags for the project
    """

    name: str
    description: str
    tags: "ProjectInTags"
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        name = self.name
        description = self.description
        tags = self.tags.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "description": description,
                "tags": tags,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.project_in_tags import ProjectInTags

        d = src_dict.copy()
        name = d.pop("name")

        description = d.pop("description")

        tags = ProjectInTags.from_dict(d.pop("tags"))

        project_in = cls(
            name=name,
            description=description,
            tags=tags,
        )

        project_in.additional_properties = d
        return project_in

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
