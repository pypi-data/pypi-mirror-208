import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

import attr
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.project_out_tags import ProjectOutTags
    from ..models.visibility_full import VisibilityFull


T = TypeVar("T", bound="ProjectOut")


@attr.s(auto_attribs=True)
class ProjectOut:
    """
    Attributes:
        name (str):
        description (str):
        tags (ProjectOutTags):
        created_at (datetime.datetime):
        updated_at (datetime.datetime):
        owner (str):
        permissions (VisibilityFull):
        id (Union[Unset, int]):
        slug (Union[Unset, str]):
    """

    name: str
    description: str
    tags: "ProjectOutTags"
    created_at: datetime.datetime
    updated_at: datetime.datetime
    owner: str
    permissions: "VisibilityFull"
    id: Union[Unset, int] = UNSET
    slug: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        name = self.name
        description = self.description
        tags = self.tags.to_dict()

        created_at = self.created_at.isoformat()

        updated_at = self.updated_at.isoformat()

        owner = self.owner
        permissions = self.permissions.to_dict()

        id = self.id
        slug = self.slug

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "description": description,
                "tags": tags,
                "created_at": created_at,
                "updated_at": updated_at,
                "owner": owner,
                "permissions": permissions,
            }
        )
        if id is not UNSET:
            field_dict["id"] = id
        if slug is not UNSET:
            field_dict["slug"] = slug

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.project_out_tags import ProjectOutTags
        from ..models.visibility_full import VisibilityFull

        d = src_dict.copy()
        name = d.pop("name")

        description = d.pop("description")

        tags = ProjectOutTags.from_dict(d.pop("tags"))

        created_at = isoparse(d.pop("created_at"))

        updated_at = isoparse(d.pop("updated_at"))

        owner = d.pop("owner")

        permissions = VisibilityFull.from_dict(d.pop("permissions"))

        id = d.pop("id", UNSET)

        slug = d.pop("slug", UNSET)

        project_out = cls(
            name=name,
            description=description,
            tags=tags,
            created_at=created_at,
            updated_at=updated_at,
            owner=owner,
            permissions=permissions,
            id=id,
            slug=slug,
        )

        project_out.additional_properties = d
        return project_out

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
