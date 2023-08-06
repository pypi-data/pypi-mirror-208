from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

import attr

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.documentation_asset_out_documentation import DocumentationAssetOutDocumentation


T = TypeVar("T", bound="DocumentationAssetOut")


@attr.s(auto_attribs=True)
class DocumentationAssetOut:
    """
    Attributes:
        project (int):
        name (str):
        documentation_type (str):
        documentation (DocumentationAssetOutDocumentation):
        documentation_schema (int):
        id (Union[Unset, int]):
    """

    project: int
    name: str
    documentation_type: str
    documentation: "DocumentationAssetOutDocumentation"
    documentation_schema: int
    id: Union[Unset, int] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        project = self.project
        name = self.name
        documentation_type = self.documentation_type
        documentation = self.documentation.to_dict()

        documentation_schema = self.documentation_schema
        id = self.id

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "project": project,
                "name": name,
                "documentation_type": documentation_type,
                "documentation": documentation,
                "documentation_schema": documentation_schema,
            }
        )
        if id is not UNSET:
            field_dict["id"] = id

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.documentation_asset_out_documentation import (
            DocumentationAssetOutDocumentation,
        )

        d = src_dict.copy()
        project = d.pop("project")

        name = d.pop("name")

        documentation_type = d.pop("documentation_type")

        documentation = DocumentationAssetOutDocumentation.from_dict(d.pop("documentation"))

        documentation_schema = d.pop("documentation_schema")

        id = d.pop("id", UNSET)

        documentation_asset_out = cls(
            project=project,
            name=name,
            documentation_type=documentation_type,
            documentation=documentation,
            documentation_schema=documentation_schema,
            id=id,
        )

        documentation_asset_out.additional_properties = d
        return documentation_asset_out

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
