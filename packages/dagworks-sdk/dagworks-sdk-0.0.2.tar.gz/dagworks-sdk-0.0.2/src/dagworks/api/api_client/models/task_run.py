import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union, cast

import attr
from dateutil.parser import isoparse

from ..models.task_run_status import TaskRunStatus
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.task_run_result_summary import TaskRunResultSummary


T = TypeVar("T", bound="TaskRun")


@attr.s(auto_attribs=True)
class TaskRun:
    """
    Attributes:
        node_name (str):
        status (TaskRunStatus):
        start_time (datetime.datetime):
        end_time (datetime.datetime):
        result_type (str):
        result_summary (Union[Unset, TaskRunResultSummary]):
        error (Union[Unset, List[str]]):
    """

    node_name: str
    status: TaskRunStatus
    start_time: datetime.datetime
    end_time: datetime.datetime
    result_type: str
    result_summary: Union[Unset, "TaskRunResultSummary"] = UNSET
    error: Union[Unset, List[str]] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        node_name = self.node_name
        status = self.status.value

        start_time = self.start_time.isoformat()

        end_time = self.end_time.isoformat()

        result_type = self.result_type
        result_summary: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.result_summary, Unset):
            result_summary = self.result_summary.to_dict()

        error: Union[Unset, List[str]] = UNSET
        if not isinstance(self.error, Unset):
            error = self.error

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "node_name": node_name,
                "status": status,
                "start_time": start_time,
                "end_time": end_time,
                "result_type": result_type,
            }
        )
        if result_summary is not UNSET:
            field_dict["result_summary"] = result_summary
        if error is not UNSET:
            field_dict["error"] = error

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.task_run_result_summary import TaskRunResultSummary

        d = src_dict.copy()
        node_name = d.pop("node_name")

        status = TaskRunStatus(d.pop("status"))

        start_time = isoparse(d.pop("start_time"))

        end_time = isoparse(d.pop("end_time"))

        result_type = d.pop("result_type")

        _result_summary = d.pop("result_summary", UNSET)
        result_summary: Union[Unset, TaskRunResultSummary]
        if isinstance(_result_summary, Unset):
            result_summary = UNSET
        else:
            result_summary = TaskRunResultSummary.from_dict(_result_summary)

        error = cast(List[str], d.pop("error", UNSET))

        task_run = cls(
            node_name=node_name,
            status=status,
            start_time=start_time,
            end_time=end_time,
            result_type=result_type,
            result_summary=result_summary,
            error=error,
        )

        task_run.additional_properties = d
        return task_run

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
