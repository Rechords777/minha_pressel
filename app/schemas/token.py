from pydantic import BaseModel
from typing import Optional
from app.models.user import UserRole # Import UserRole

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenPayload(BaseModel):
    sub: Optional[str] = None # Corresponds to user email
    user_id: Optional[int] = None
    role: Optional[UserRole] = None

