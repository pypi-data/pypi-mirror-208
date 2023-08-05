from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

import attr

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.run_log_out import RunLogOut


T = TypeVar("T", bound="PagedRunLogOut")


@attr.s(auto_attribs=True)
class PagedRunLogOut:
    """
    Attributes:
        count (int):
        items (Union[Unset, List['RunLogOut']]):
    """

    count: int
    items: Union[Unset, List["RunLogOut"]] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        count = self.count
        items: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.items, Unset):
            items = []
            for items_item_data in self.items:
                items_item = items_item_data.to_dict()

                items.append(items_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "count": count,
            }
        )
        if items is not UNSET:
            field_dict["items"] = items

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.run_log_out import RunLogOut

        d = src_dict.copy()
        count = d.pop("count")

        items = []
        _items = d.pop("items", UNSET)
        for items_item_data in _items or []:
            items_item = RunLogOut.from_dict(items_item_data)

            items.append(items_item)

        paged_run_log_out = cls(
            count=count,
            items=items,
        )

        paged_run_log_out.additional_properties = d
        return paged_run_log_out

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
