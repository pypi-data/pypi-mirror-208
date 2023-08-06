from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar

import attr

if TYPE_CHECKING:
    from ..models.organization_out import OrganizationOut
    from ..models.user_out import UserOut


T = TypeVar("T", bound="WhoAmIResult")


@attr.s(auto_attribs=True)
class WhoAmIResult:
    """
    Attributes:
        user (UserOut):
        organizations (List['OrganizationOut']):
    """

    user: "UserOut"
    organizations: List["OrganizationOut"]
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        user = self.user.to_dict()

        organizations = []
        for organizations_item_data in self.organizations:
            organizations_item = organizations_item_data.to_dict()

            organizations.append(organizations_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "user": user,
                "organizations": organizations,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.organization_out import OrganizationOut
        from ..models.user_out import UserOut

        d = src_dict.copy()
        user = UserOut.from_dict(d.pop("user"))

        organizations = []
        _organizations = d.pop("organizations")
        for organizations_item_data in _organizations:
            organizations_item = OrganizationOut.from_dict(organizations_item_data)

            organizations.append(organizations_item)

        who_am_i_result = cls(
            user=user,
            organizations=organizations,
        )

        who_am_i_result.additional_properties = d
        return who_am_i_result

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
