from enum import Enum


class TaskRunStatus(str, Enum):
    FAILURE = "FAILURE"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    UNINITIALIZED = "UNINITIALIZED"

    def __str__(self) -> str:
        return str(self.value)
