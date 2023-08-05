from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union, cast

import attr

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.hamilton_node_dependencies import HamiltonNodeDependencies
    from ..models.hamilton_node_tags import HamiltonNodeTags
    from ..models.python_type import PythonType


T = TypeVar("T", bound="HamiltonNode")


@attr.s(auto_attribs=True)
class HamiltonNode:
    """Represents a hamilton Node -- stores a pointer to  function

    Attributes:
        name (str):
        function_identifier (List[str]):
        dependencies (HamiltonNodeDependencies):
        tags (HamiltonNodeTags):
        namespace (List[str]):
        user_defined (bool):
        return_type (PythonType): Represents a python type
        documentation (Union[Unset, str]):
    """

    name: str
    function_identifier: List[str]
    dependencies: "HamiltonNodeDependencies"
    tags: "HamiltonNodeTags"
    namespace: List[str]
    user_defined: bool
    return_type: "PythonType"
    documentation: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        name = self.name
        function_identifier = self.function_identifier

        dependencies = self.dependencies.to_dict()

        tags = self.tags.to_dict()

        namespace = self.namespace

        user_defined = self.user_defined
        return_type = self.return_type.to_dict()

        documentation = self.documentation

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "functionIdentifier": function_identifier,
                "dependencies": dependencies,
                "tags": tags,
                "namespace": namespace,
                "userDefined": user_defined,
                "returnType": return_type,
            }
        )
        if documentation is not UNSET:
            field_dict["documentation"] = documentation

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.hamilton_node_dependencies import HamiltonNodeDependencies
        from ..models.hamilton_node_tags import HamiltonNodeTags
        from ..models.python_type import PythonType

        d = src_dict.copy()
        name = d.pop("name")

        function_identifier = cast(List[str], d.pop("functionIdentifier"))

        dependencies = HamiltonNodeDependencies.from_dict(d.pop("dependencies"))

        tags = HamiltonNodeTags.from_dict(d.pop("tags"))

        namespace = cast(List[str], d.pop("namespace"))

        user_defined = d.pop("userDefined")

        return_type = PythonType.from_dict(d.pop("returnType"))

        documentation = d.pop("documentation", UNSET)

        hamilton_node = cls(
            name=name,
            function_identifier=function_identifier,
            dependencies=dependencies,
            tags=tags,
            namespace=namespace,
            user_defined=user_defined,
            return_type=return_type,
            documentation=documentation,
        )

        hamilton_node.additional_properties = d
        return hamilton_node

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
