from pydantic import BaseModel, HttpUrl
from typing import Optional, List
from datetime import datetime
from app.models.presell import PresellType, PresellStatus
from app.schemas.user import User # To show owner info

# Shared properties
class PresellBase(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None
    presell_type: Optional[PresellType] = None
    affiliate_link: Optional[HttpUrl] = None
    product_url: Optional[HttpUrl] = None
    language_code: Optional[str] = "pt"
    custom_background_image_url: Optional[str] = None # Add field for custom background

# Properties to receive via API on creation
class PresellCreate(PresellBase):
    name: str
    slug: str # Consider adding validation for slug format (e.g., no spaces, lowercase)
    presell_type: PresellType
    affiliate_link: HttpUrl
    product_url: HttpUrl
    language_code: str = "pt"

# Properties to receive via API on update
class PresellUpdate(PresellBase):
    name: Optional[str] = None
    slug: Optional[str] = None
    presell_type: Optional[PresellType] = None
    affiliate_link: Optional[HttpUrl] = None
    product_url: Optional[HttpUrl] = None
    language_code: Optional[str] = None
    status: Optional[PresellStatus] = None # Allow updating status

class PresellInDBBase(PresellBase):
    id: int
    owner_id: Optional[int] = None
    public_url: Optional[str] = None
    screenshot_path: Optional[str] = None # Placeholder path
    custom_background_image_url: Optional[str] = None # Add field here too
    generated_html_path: Optional[str] = None
    status: PresellStatus = PresellStatus.RASCUNHO
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True # Pydantic V1, use from_attributes = True for V2

# Additional properties to return via API
class Presell(PresellInDBBase):
    owner: Optional[User] = None # Include owner details

# Properties for the public page generation (internal use or specific endpoint)
class PresellPublicData(BaseModel):
    affiliate_link: HttpUrl
    language_code: str
    # Add other fields needed by the presell template, e.g., translated texts
    # translated_texts: dict 

