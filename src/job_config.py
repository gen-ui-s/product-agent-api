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
    ANDROID_COMPACT = DeviceSize(width=412, height=917, corner_radius=28, name="Android Compact")
    ANDROID_MEDIUM = DeviceSize(width=700, height=840, corner_radius=28, name="Android Medium")
    IPHONE_16 = DeviceSize(width=393, height=852, corner_radius=33, name="iPhone 16")
    IPHONE_16_PRO = DeviceSize(width=402, height=874, corner_radius=33, name="iPhone 16 Pro")
    IPHONE_16_PRO_MAX = DeviceSize(width=430, height=956, corner_radius=33, name="iPhone 16 Pro Max")
    IPHONE_16_PLUS = DeviceSize(width=430, height=932, corner_radius=33, name="iPhone 16 Plus")
    IPHONE_15_14_PRO_MAX = DeviceSize(width=430, height=932, corner_radius=33, name="iPhone 15/14 Pro Max")
    IPHONE_15_14_PRO = DeviceSize(width=393, height=852, corner_radius=33, name="iPhone 15/14 Pro")
    IPHONE_13_14 = DeviceSize(width=390, height=844, corner_radius=33, name="iPhone 13/14")
    IPHONE_14_PLUS = DeviceSize(width=428, height=926, corner_radius=33, name="iPhone 14 Plus")
    IPHONE_13_MINI = DeviceSize(width=375, height=812, corner_radius=33, name="iPhone 13 Mini")
    IPHONE_SE = DeviceSize(width=320, height=568, corner_radius=33, name="iPhone SE")
    
    # Desktops / slides / TV
    MACBOOK_AIR = DeviceSize(width=1280, height=832, corner_radius=24, name="MacBook Air")
    MACBOOK_PRO_14 = DeviceSize(width=1512, height=982, corner_radius=24, name="MacBook Pro 14")
    MACBOOK_PRO_16 = DeviceSize(width=1728, height=1117, corner_radius=24, name="MacBook Pro 16")
    DESKTOP = DeviceSize(width=1440, height=1024, corner_radius=24, name="Desktop")
    WIREFRAMES = DeviceSize(width=1440, height=1024, corner_radius=24, name="Wireframes")
    TV = DeviceSize(width=1280, height=720, corner_radius=24, name="TV")
    SLIDE_16_9 = DeviceSize(width=1920, height=1080, corner_radius=24, name="Slide 16:9")
    SLIDE_4_3 = DeviceSize(width=1024, height=768, corner_radius=24, name="Slide 4:3")
   
    @classmethod
    def get_device_names(cls):
        return {
            device.value.name: {
                "width": device.value.width,
                "height": device.value.height,
                "corner_radius": device.value.corner_radius,
                "platform": device.value.platform
            }
            for device in cls
        }

    @classmethod
    def get_device_by_name(cls, name: str) -> DeviceSize:
        for device in cls:
            if device.value.name == name:
                return device.value
        raise ValueError(f"Device with name '{name}' not found.")
