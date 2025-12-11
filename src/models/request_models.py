from pydantic import BaseModel


class Component(BaseModel):
    id: str
    code: str