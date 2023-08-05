from typing import Any, Dict, List, Type, TypeVar, Union, cast

import attr

from ..types import UNSET, Unset

T = TypeVar("T", bound="HamiltonFunction")


@attr.s(auto_attribs=True)
class HamiltonFunction:
    """Represents a python function that could produce to multiple nodes

    Attributes:
        name (str):
        module (List[str]):
        contents (str):
        line_start (int):
        line_end (int):
        file (Union[Unset, str]):  Default: ''.
    """

    name: str
    module: List[str]
    contents: str
    line_start: int
    line_end: int
    file: Union[Unset, str] = ""
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        name = self.name
        module = self.module

        contents = self.contents
        line_start = self.line_start
        line_end = self.line_end
        file = self.file

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "module": module,
                "contents": contents,
                "lineStart": line_start,
                "lineEnd": line_end,
            }
        )
        if file is not UNSET:
            field_dict["file"] = file

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        name = d.pop("name")

        module = cast(List[str], d.pop("module"))

        contents = d.pop("contents")

        line_start = d.pop("lineStart")

        line_end = d.pop("lineEnd")

        file = d.pop("file", UNSET)

        hamilton_function = cls(
            name=name,
            module=module,
            contents=contents,
            line_start=line_start,
            line_end=line_end,
            file=file,
        )

        hamilton_function.additional_properties = d
        return hamilton_function

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
