from typing import Any, Dict, List, Type, TypeVar, cast

import attr

T = TypeVar("T", bound="VisibilityIn")


@attr.s(auto_attribs=True)
class VisibilityIn:
    """
    Attributes:
        user_ids_visible (List[int]):
        organization_ids_visible (List[int]):
        user_ids_writable (List[int]):
        organization_ids_writable (List[int]):
    """

    user_ids_visible: List[int]
    organization_ids_visible: List[int]
    user_ids_writable: List[int]
    organization_ids_writable: List[int]
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        user_ids_visible = self.user_ids_visible

        organization_ids_visible = self.organization_ids_visible

        user_ids_writable = self.user_ids_writable

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
        user_ids_visible = cast(List[int], d.pop("user_ids_visible"))

        organization_ids_visible = cast(List[int], d.pop("organization_ids_visible"))

        user_ids_writable = cast(List[int], d.pop("user_ids_writable"))

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
