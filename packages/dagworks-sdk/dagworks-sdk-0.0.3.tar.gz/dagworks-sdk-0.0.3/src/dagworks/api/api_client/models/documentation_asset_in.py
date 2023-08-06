from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar

import attr

if TYPE_CHECKING:
    from ..models.documentation_asset_in_documentation import DocumentationAssetInDocumentation


T = TypeVar("T", bound="DocumentationAssetIn")


@attr.s(auto_attribs=True)
class DocumentationAssetIn:
    """
    Attributes:
        name (str): The name of the documentation asset
        documentation_type (str): The type of documentation asset
        documentation (DocumentationAssetInDocumentation): The documentation asset
        documentation_schema (int): The schema version of the documentation asset
    """

    name: str
    documentation_type: str
    documentation: "DocumentationAssetInDocumentation"
    documentation_schema: int
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        name = self.name
        documentation_type = self.documentation_type
        documentation = self.documentation.to_dict()

        documentation_schema = self.documentation_schema

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "documentation_type": documentation_type,
                "documentation": documentation,
                "documentation_schema": documentation_schema,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.documentation_asset_in_documentation import DocumentationAssetInDocumentation

        d = src_dict.copy()
        name = d.pop("name")

        documentation_type = d.pop("documentation_type")

        documentation = DocumentationAssetInDocumentation.from_dict(d.pop("documentation"))

        documentation_schema = d.pop("documentation_schema")

        documentation_asset_in = cls(
            name=name,
            documentation_type=documentation_type,
            documentation=documentation,
            documentation_schema=documentation_schema,
        )

        documentation_asset_in.additional_properties = d
        return documentation_asset_in

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
