from pydantic import BaseModel

class Message(BaseModel):
    type: str
    content: str