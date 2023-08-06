from typing import Any, Dict, List, Type, TypeVar, Union, cast

import attr

T = TypeVar("T", bound="VisibilityIn")


@attr.s(auto_attribs=True)
class VisibilityIn:
    """
    Attributes:
        user_ids_visible (List[Union[int, str]]):
        organization_ids_visible (List[int]):
        user_ids_writable (List[Union[int, str]]):
        organization_ids_writable (List[int]):
    """

    user_ids_visible: List[Union[int, str]]
    organization_ids_visible: List[int]
    user_ids_writable: List[Union[int, str]]
    organization_ids_writable: List[int]
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        user_ids_visible = []
        for user_ids_visible_item_data in self.user_ids_visible:
            user_ids_visible_item: Union[int, str]

            user_ids_visible_item = user_ids_visible_item_data

            user_ids_visible.append(user_ids_visible_item)

        organization_ids_visible = self.organization_ids_visible

        user_ids_writable = []
        for user_ids_writable_item_data in self.user_ids_writable:
            user_ids_writable_item: Union[int, str]

            user_ids_writable_item = user_ids_writable_item_data

            user_ids_writable.append(user_ids_writable_item)

        organization_ids_writable = self.organization_ids_writable

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "user_ids_visible": user_ids_visible,
                "organization_ids_visible": organization_ids_visible,
                "user_ids_writable": user_ids_writable,
                "organization_ids_writable": organization_ids_writable,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        user_ids_visible = []
        _user_ids_visible = d.pop("user_ids_visible")
        for user_ids_visible_item_data in _user_ids_visible:

            def _parse_user_ids_visible_item(data: object) -> Union[int, str]:
                return cast(Union[int, str], data)

            user_ids_visible_item = _parse_user_ids_visible_item(user_ids_visible_item_data)

            user_ids_visible.append(user_ids_visible_item)

        organization_ids_visible = cast(List[int], d.pop("organization_ids_visible"))

        user_ids_writable = []
        _user_ids_writable = d.pop("user_ids_writable")
        for user_ids_writable_item_data in _user_ids_writable:

            def _parse_user_ids_writable_item(data: object) -> Union[int, str]:
                return cast(Union[int, str], data)

            user_ids_writable_item = _parse_user_ids_writable_item(user_ids_writable_item_data)

            user_ids_writable.append(user_ids_writable_item)

        organization_ids_writable = cast(List[int], d.pop("organization_ids_writable"))

        visibility_in = cls(
            user_ids_visible=user_ids_visible,
            organization_ids_visible=organization_ids_visible,
            user_ids_writable=user_ids_writable,
            organization_ids_writable=organization_ids_writable,
        )

        visibility_in.additional_properties = d
        return visibility_in

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
