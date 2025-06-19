from sqlalchemy.orm import Session
from typing import List, Optional, Any, Dict
from fastapi.encoders import jsonable_encoder

from app.models.presell import Presell
from app.schemas.presell import PresellCreate, PresellUpdate, PresellStatus

def get_presell(db: Session, presell_id: int, owner_id: Optional[int] = None) -> Optional[Presell]:
    """
    Get a presell by ID.
    If owner_id is provided, also filter by owner.
    """
    query = db.query(Presell).filter(Presell.id == presell_id)
    if owner_id is not None:
        query = query.filter(Presell.owner_id == owner_id)
    return query.first()

def get_presell_by_slug(db: Session, slug: str) -> Optional[Presell]:
    """
    Get a presell by slug.
    """
    return db.query(Presell).filter(Presell.slug == slug).first()

def get_all_presells(db: Session, skip: int = 0, limit: int = 100) -> List[Presell]:
    """
    Get all presells with pagination.
    """
    return db.query(Presell).offset(skip).limit(limit).all()

def get_presells_by_owner(db: Session, owner_id: int, skip: int = 0, limit: int = 100) -> List[Presell]:
    """
    Get presells by owner with pagination.
    """
    return db.query(Presell).filter(Presell.owner_id == owner_id).offset(skip).limit(limit).all()

def create_presell(db: Session, presell: PresellCreate, owner_id: Optional[int] = None) -> Presell:
    """
    Create a new presell.
    """
    db_presell = Presell(
        presell_type=presell.presell_type,
        affiliate_link=presell.affiliate_link,
        product_url=presell.product_url,
        language_code=presell.language_code,
        slug=presell.slug,
        owner_id=owner_id,
        status=PresellStatus.RASCUNHO,
        custom_background_image_url=presell.custom_background_image_url  # Add custom background image URL
    )
    db.add(db_presell)
    db.commit()
    db.refresh(db_presell)
    return db_presell

def update_presell(db: Session, db_presell: Presell, presell_in: PresellUpdate) -> Presell:
    """
    Update a presell.
    """
    obj_data = jsonable_encoder(db_presell)
    update_data = presell_in.dict(exclude_unset=True)
    for field in obj_data:
        if field in update_data:
            setattr(db_presell, field, update_data[field])
    db.add(db_presell)
    db.commit()
    db.refresh(db_presell)
    return db_presell

def update_presell_generated_info(
    db: Session, 
    db_presell: Presell, 
    screenshot_path: Optional[str] = None,
    generated_html_path: Optional[str] = None,
    public_url: Optional[str] = None,
    status: Optional[PresellStatus] = None
) -> Presell:
    """
    Update a presell with generated assets info.
    """
    if screenshot_path is not None:
        db_presell.screenshot_path = screenshot_path
    if generated_html_path is not None:
        db_presell.generated_html_path = generated_html_path
    if public_url is not None:
        db_presell.public_url = public_url
    if status is not None:
        db_presell.status = status
    
    db.add(db_presell)
    db.commit()
    db.refresh(db_presell)
    return db_presell

def delete_presell(db: Session, presell_id: int, owner_id: Optional[int] = None) -> Presell:
    """
    Delete a presell.
    If owner_id is provided, also filter by owner.
    """
    query = db.query(Presell).filter(Presell.id == presell_id)
    if owner_id is not None:
        query = query.filter(Presell.owner_id == owner_id)
    
    db_presell = query.first()
    if db_presell:
        db.delete(db_presell)
        db.commit()
    return db_presell
