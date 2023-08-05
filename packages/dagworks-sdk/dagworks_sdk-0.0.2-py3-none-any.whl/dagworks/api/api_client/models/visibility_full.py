from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar

import attr

if TYPE_CHECKING:
    from ..models.organization_out import OrganizationOut
    from ..models.user_out import UserOut


T = TypeVar("T", bound="VisibilityFull")


@attr.s(auto_attribs=True)
class VisibilityFull:
    """
    Attributes:
        user_visible (List['UserOut']):
        organization_visible (List['OrganizationOut']):
        user_writable (List['UserOut']):
        organization_writable (List['OrganizationOut']):
    """

    user_visible: List["UserOut"]
    organization_visible: List["OrganizationOut"]
    user_writable: List["UserOut"]
    organization_writable: List["OrganizationOut"]
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        user_visible = []
        for user_visible_item_data in self.user_visible:
            user_visible_item = user_visible_item_data.to_dict()

            user_visible.append(user_visible_item)

        organization_visible = []
        for organization_visible_item_data in self.organization_visible:
            organization_visible_item = organization_visible_item_data.to_dict()

            organization_visible.append(organization_visible_item)

        user_writable = []
        for user_writable_item_data in self.user_writable:
            user_writable_item = user_writable_item_data.to_dict()

            user_writable.append(user_writable_item)

        organization_writable = []
        for organization_writable_item_data in self.organization_writable:
            organization_writable_item = organization_writable_item_data.to_dict()

            organization_writable.append(organization_writable_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "user_visible": user_visible,
                "organization_visible": organization_visible,
                "user_writable": user_writable,
                "organization_writable": organization_writable,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.organization_out import OrganizationOut
        from ..models.user_out import UserOut

        d = src_dict.copy()
        user_visible = []
        _user_visible = d.pop("user_visible")
        for user_visible_item_data in _user_visible:
            user_visible_item = UserOut.from_dict(user_visible_item_data)

            user_visible.append(user_visible_item)

        organization_visible = []
        _organization_visible = d.pop("organization_visible")
        for organization_visible_item_data in _organization_visible:
            organization_visible_item = OrganizationOut.from_dict(organization_visible_item_data)

            organization_visible.append(organization_visible_item)

        user_writable = []
        _user_writable = d.pop("user_writable")
        for user_writable_item_data in _user_writable:
            user_writable_item = UserOut.from_dict(user_writable_item_data)

            user_writable.append(user_writable_item)

        organization_writable = []
        _organization_writable = d.pop("organization_writable")
        for organization_writable_item_data in _organization_writable:
            organization_writable_item = OrganizationOut.from_dict(organization_writable_item_data)

            organization_writable.append(organization_writable_item)

        visibility_full = cls(
            user_visible=user_visible,
            organization_visible=organization_visible,
            user_writable=user_writable,
            organization_writable=organization_writable,
        )

        visibility_full.additional_properties = d
        return visibility_full

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
