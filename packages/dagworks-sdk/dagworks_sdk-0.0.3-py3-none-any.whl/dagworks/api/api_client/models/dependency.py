from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar

import attr

if TYPE_CHECKING:
    from ..models.python_type import PythonType


T = TypeVar("T", bound="Dependency")


@attr.s(auto_attribs=True)
class Dependency:
    """Represents a dependency of a node

    Attributes:
        type (PythonType): Represents a python type
        name (str):
        dependency_type (str):
    """

    type: "PythonType"
    name: str
    dependency_type: str
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        type = self.type.to_dict()

        name = self.name
        dependency_type = self.dependency_type

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "type": type,
                "name": name,
                "dependencyType": dependency_type,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.python_type import PythonType

        d = src_dict.copy()
        type = PythonType.from_dict(d.pop("type"))

        name = d.pop("name")

        dependency_type = d.pop("dependencyType")

        dependency = cls(
            type=type,
            name=name,
            dependency_type=dependency_type,
        )

        dependency.additional_properties = d
        return dependency

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
