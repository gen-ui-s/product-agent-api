from pydantic import BaseModel


class GenerateComponentRequest(BaseModel):
    prompt: str
    user_id: str

class Component(BaseModel):
    id: str
    code: str