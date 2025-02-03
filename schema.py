from pydantic import BaseModel # type: ignore
from typing import Optional, List

class UserCreate(BaseModel):
    user_id: int
    name: str
    email: str

class Message(BaseModel):
    user_id: int
    message_id: int
    message: str
    response: Optional[str] = None

class UserHistory(BaseModel):
    user_id: int
    history: list[Message]