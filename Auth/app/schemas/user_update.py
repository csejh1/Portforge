from typing import Optional, List
from pydantic import BaseModel
from app.models.enums import UserRole, StackCategory, TechStack
from app.schemas.user import UserSimple

class UserUpdate(BaseModel):
    name: Optional[str] = None
    myStacks: Optional[List[str]] = None

    class Config:
        from_attributes = True
