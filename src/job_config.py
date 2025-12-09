from enum import Enum
from dataclasses import dataclass


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
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    SUCCESSFUL = "SUCCESSFUL"
    FAILED = "FAILED"


@dataclass
class DeviceSize:
    name: str
    width: int
    height: int
    corner_radius: int


class AvailableDeviceSizes(Enum):
    IPHONE_14_PRO = DeviceSize(name="iPhone 14 Pro", width=393, height=852, corner_radius=55)
    PIXEL_7 = DeviceSize(name="Pixel 7", width=412, height=915, corner_radius=24)
    GALAXY_S23 = DeviceSize(name="Galaxy S23", width=360, height=780, corner_radius=20)

