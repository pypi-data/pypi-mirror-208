from enum import Enum


class TaskRunStatus(str, Enum):
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    RUNNING = "RUNNING"
    UNINITIALIZED = "UNINITIALIZED"

    def __str__(self) -> str:
        return str(self.value)
