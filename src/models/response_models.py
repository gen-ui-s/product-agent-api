from pydantic import BaseModel
import json
from typing import Optional


class ResponseModel(BaseModel):
    status_code: int
    message: Optional[str] = None
    error: Optional[str] = None