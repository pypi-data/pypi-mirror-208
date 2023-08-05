from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar

import attr

if TYPE_CHECKING:
    from ..models.project_in import ProjectIn
    from ..models.visibility_in import VisibilityIn


T = TypeVar("T", bound="TrackingserverApiApiUpdateProjectBodyParams")


@attr.s(auto_attribs=True)
class TrackingserverApiApiUpdateProjectBodyParams:
    """
    Attributes:
        project (ProjectIn):
        visibility (VisibilityIn):
    """

    project: "ProjectIn"
    visibility: "VisibilityIn"
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        project = self.project.to_dict()

        visibility = self.visibility.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "project": project,
                "visibility": visibility,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.project_in import ProjectIn
        from ..models.visibility_in import VisibilityIn

        d = src_dict.copy()
        project = ProjectIn.from_dict(d.pop("project"))

        visibility = VisibilityIn.from_dict(d.pop("visibility"))

        trackingserver_api_api_update_project_body_params = cls(
            project=project,
            visibility=visibility,
        )

        trackingserver_api_api_update_project_body_params.additional_properties = d
        return trackingserver_api_api_update_project_body_params

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
