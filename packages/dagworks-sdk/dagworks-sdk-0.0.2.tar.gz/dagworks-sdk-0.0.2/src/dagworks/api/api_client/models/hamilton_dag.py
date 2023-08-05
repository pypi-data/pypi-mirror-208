from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, cast

import attr

if TYPE_CHECKING:
    from ..models.hamilton_function import HamiltonFunction
    from ..models.hamilton_node import HamiltonNode


T = TypeVar("T", bound="HamiltonDAG")


@attr.s(auto_attribs=True)
class HamiltonDAG:
    """Represents a logical DAG

    Attributes:
        functions (List['HamiltonFunction']):
        nodes (List['HamiltonNode']):
        dag_root (List[str]):
    """

    functions: List["HamiltonFunction"]
    nodes: List["HamiltonNode"]
    dag_root: List[str]
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        functions = []
        for functions_item_data in self.functions:
            functions_item = functions_item_data.to_dict()

            functions.append(functions_item)

        nodes = []
        for nodes_item_data in self.nodes:
            nodes_item = nodes_item_data.to_dict()

            nodes.append(nodes_item)

        dag_root = self.dag_root

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "functions": functions,
                "nodes": nodes,
                "DAGRoot": dag_root,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.hamilton_function import HamiltonFunction
        from ..models.hamilton_node import HamiltonNode

        d = src_dict.copy()
        functions = []
        _functions = d.pop("functions")
        for functions_item_data in _functions:
            functions_item = HamiltonFunction.from_dict(functions_item_data)

            functions.append(functions_item)

        nodes = []
        _nodes = d.pop("nodes")
        for nodes_item_data in _nodes:
            nodes_item = HamiltonNode.from_dict(nodes_item_data)

            nodes.append(nodes_item)

        dag_root = cast(List[str], d.pop("DAGRoot"))

        hamilton_dag = cls(
            functions=functions,
            nodes=nodes,
            dag_root=dag_root,
        )

        hamilton_dag.additional_properties = d
        return hamilton_dag

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
