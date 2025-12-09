from dataclasses import dataclass
from typing import Optional, Dict
from job_config import JobStatus, ComponentStatus, AvailablePlatforms, GenerationType, DeviceSize, AvailableDeviceSizes

@dataclass 
class User:
    _id: str
    auth0_sub: str
    given_name: str
    email: str
    credits: int
    subscription_status: str
    stripe_customer_id: Optional[str] = None
    created_at: Optional[str] = ""
    updated_at: Optional[str] = ""
    
    def to_dict(self):
        return {
            "_id": self._id,
            "auth0_sub": self.auth0_sub,
            "given_name": self.given_name,
            "email": self.email,
            "credits": self.credits,
            "subscription_status": self.subscription_status,
            "stripe_customer_id": self.stripe_customer_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }


@dataclass
class Job:
    _id: str
    user_prompt: str
    user_id: str
    status: JobStatus
    screen_count: int
    model: str
    device: AvailableDeviceSizes
    generation_type: GenerationType
    created_at: str
    platform: Optional[AvailablePlatforms] = None
    optimized_prompt: Optional[str] = None
    completed_at: Optional[str] = None
    error_message: Optional[str] = None
    
    def to_dict(self):
        return {
            "_id": self._id,
            "user_prompt": self.user_prompt,
            "user_id": self.user_id,
            "status": self.status,
            "screen_count": self.screen_count,
            "model": self.model,
            "device": self.device
            "platform": self.platform,
            "generation_type": self.generation_type,
            "optimized_prompt": self.optimized_prompt,
            "created_at": self.created_at,
            "completed_at": self.completed_at,
            "error_message": self.error_message
        }

  
@dataclass
class Component:
    _id: str
    parent_job_id: str
    status: ComponentStatus
    sub_prompt: Optional[str] = None
    completed_at: Optional[str] = None
    error_message: Optional[str] = None
    code: Optional[str] = None
    
    def to_dict(self):
        return {
            "_id": self._id,
            "parent_job_id": self.parent_job_id,
            "status": self.status.value,
            "sub_prompt": self.sub_prompt,
            "completed_at": self.completed_at,
            "error_message": self.error_message,
            "code": self.code
        }
