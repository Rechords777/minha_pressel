from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Enum as SQLAlchemyEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.db.session import Base

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    AFILIADO = "afiliado"
    VISUALIZADOR = "visualizador"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, index=True)
    is_active = Column(Boolean(), default=True)
    role = Column(SQLAlchemyEnum(UserRole), default=UserRole.AFILIADO, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    presells = relationship("Presell", back_populates="owner")

