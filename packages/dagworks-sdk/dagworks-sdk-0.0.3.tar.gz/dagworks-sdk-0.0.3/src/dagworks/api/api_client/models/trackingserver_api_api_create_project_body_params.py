from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

import attr

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.documentation_asset_in import DocumentationAssetIn
    from ..models.project_in import ProjectIn
    from ..models.visibility_in import VisibilityIn


T = TypeVar("T", bound="TrackingserverApiApiCreateProjectBodyParams")


@attr.s(auto_attribs=True)
class TrackingserverApiApiCreateProjectBodyParams:
    """
    Attributes:
        project (ProjectIn):
        visibility (VisibilityIn):
        documentation (Union[Unset, List['DocumentationAssetIn']]):
    """

    project: "ProjectIn"
    visibility: "VisibilityIn"
    documentation: Union[Unset, List["DocumentationAssetIn"]] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        project = self.project.to_dict()

        visibility = self.visibility.to_dict()

        documentation: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.documentation, Unset):
            documentation = []
            for documentation_item_data in self.documentation:
                documentation_item = documentation_item_data.to_dict()

                documentation.append(documentation_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "project": project,
                "visibility": visibility,
            }
        )
        if documentation is not UNSET:
            field_dict["documentation"] = documentation

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.documentation_asset_in import DocumentationAssetIn
        from ..models.project_in import ProjectIn
        from ..models.visibility_in import VisibilityIn

        d = src_dict.copy()
        project = ProjectIn.from_dict(d.pop("project"))

        visibility = VisibilityIn.from_dict(d.pop("visibility"))

        documentation = []
        _documentation = d.pop("documentation", UNSET)
        for documentation_item_data in _documentation or []:
            documentation_item = DocumentationAssetIn.from_dict(documentation_item_data)

            documentation.append(documentation_item)

        trackingserver_api_api_create_project_body_params = cls(
            project=project,
            visibility=visibility,
            documentation=documentation,
        )

        trackingserver_api_api_create_project_body_params.additional_properties = d
        return trackingserver_api_api_create_project_body_params

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
