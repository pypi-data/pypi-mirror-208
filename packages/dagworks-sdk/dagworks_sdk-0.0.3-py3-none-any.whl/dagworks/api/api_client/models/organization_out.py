from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..types import UNSET, Unset

T = TypeVar("T", bound="OrganizationOut")


@attr.s(auto_attribs=True)
class OrganizationOut:
    """
    Attributes:
        name (str):
        propel_auth_org_id (str):
        id (Union[Unset, int]):
    """

    name: str
    propel_auth_org_id: str
    id: Union[Unset, int] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        name = self.name
        propel_auth_org_id = self.propel_auth_org_id
        id = self.id

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "propel_auth_org_id": propel_auth_org_id,
            }
        )
        if id is not UNSET:
            field_dict["id"] = id

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        name = d.pop("name")

        propel_auth_org_id = d.pop("propel_auth_org_id")

        id = d.pop("id", UNSET)

        organization_out = cls(
            name=name,
            propel_auth_org_id=propel_auth_org_id,
            id=id,
        )

        organization_out.additional_properties = d
        return organization_out

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
