from enum import Enum


class ArbexStatus(str, Enum):
    CRASH_LOOP = "crash_loop"
    FAILED = "failed"
    PENDING = "pending"
    PENDING_KILL = "pending_kill"
    RESOURCE_CONTENTION = "resource_contention"
    SCHEDULE_ERROR = "schedule_error"
    STARTED = "started"
    SUCCESS = "success"

    def __str__(self) -> str:
        return str(self.value)
