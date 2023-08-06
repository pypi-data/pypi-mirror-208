from enum import Enum


class TaskStatus(str, Enum):
    FAILURE = "failure"
    RUNNING = "running"
    SUCCESS = "success"
    UNKNOWN = "unknown"

    def __str__(self) -> str:
        return str(self.value)
