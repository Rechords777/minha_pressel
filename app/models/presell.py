from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Enum as SQLAlchemyEnum, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.db.session import Base
from app.models.user import User # Import User model for relationship

class PresellType(str, enum.Enum):
    COOKIES = "cookies"
    FANTASMA = "fantasma"
    SEXO = "sexo"
    IDADE = "idade"
    GRUPO_IDADE_HOMEM = "grupo_idade_homem"
    GRUPO_IDADE_MULHER = "grupo_idade_mulher"
    PAIS = "pais"
    CAPTCHA = "captcha"
    MODELOS = "modelos"
    # Add other types as needed, based on the MVP requirements (cookies, sexo, idade, fantasma, país)

class PresellStatus(str, enum.Enum):
    RASCUNHO = "rascunho"
    PUBLICADA = "publicada"
    ARQUIVADA = "arquivada"

class Presell(Base):
    __tablename__ = "presells"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    slug = Column(String, unique=True, index=True, nullable=False)
    presell_type = Column(SQLAlchemyEnum(PresellType), nullable=False)
    affiliate_link = Column(String, nullable=False)
    product_url = Column(String, nullable=False)
    language_code = Column(String(10), nullable=False, default="pt") # ISO 639-1 code
    
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    owner = relationship("User", back_populates="presells", foreign_keys=[owner_id])

    # Fields for generated content/status
    public_url = Column(String, nullable=True) # URL after deployment
    screenshot_path = Column(String, nullable=True) # Path to the captured screenshot (placeholder currently)
    custom_background_image_url = Column(String, nullable=True) # Path/URL to user-provided background image
    generated_html_path = Column(String, nullable=True) # Path to the generated HTML file
    status = Column(SQLAlchemyEnum(PresellStatus), default=PresellStatus.RASCUNHO, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

