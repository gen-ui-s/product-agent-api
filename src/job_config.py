from enum import Enum


class AvailablePlatforms(Enum):
    WEB = "web"
    MOBILE = "mobile"

class GenerationType(str, Enum):
    FLOW = "flow"
    ITERATION = "iteration"

class JobStatus(str, Enum):
    SUBMITTED = "SUBMITTED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"

class ComponentStatus(str, Enum):
    SUBMITTED = "SUBMITTED"
    RUNNING = "RUNNING"
    SUCCESSFUL = "SUCCESSFUL"
    FAILED = "FAILED"
