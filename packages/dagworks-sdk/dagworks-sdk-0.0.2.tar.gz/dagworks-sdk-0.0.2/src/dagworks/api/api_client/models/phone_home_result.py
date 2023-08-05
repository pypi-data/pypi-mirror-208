from typing import Any, Dict, List, Type, TypeVar

import attr

T = TypeVar("T", bound="PhoneHomeResult")


@attr.s(auto_attribs=True)
class PhoneHomeResult:
    """
    Attributes:
        success (bool): The result of the phone home
        message (str): The message associated with the result
    """

    success: bool
    message: str
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        success = self.success
        message = self.message

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "success": success,
                "message": message,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        success = d.pop("success")

        message = d.pop("message")

        phone_home_result = cls(
            success=success,
            message=message,
        )

        phone_home_result.additional_properties = d
        return phone_home_result

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
