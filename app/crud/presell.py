from sqlalchemy.orm import Session
from typing import List, Optional

from app.models.presell import Presell, PresellStatus
from app.schemas.presell import PresellCreate, PresellUpdate
from app.models.user import User

def get_presell(db: Session, presell_id: int, owner_id: Optional[int] = None) -> Optional[Presell]:
    query = db.query(Presell).filter(Presell.id == presell_id)
    if owner_id:
        query = query.filter(Presell.owner_id == owner_id)
    return query.first()

def get_presells_by_owner(db: Session, owner_id: int, skip: int = 0, limit: int = 100) -> List[Presell]:
    return db.query(Presell).filter(Presell.owner_id == owner_id).offset(skip).limit(limit).all()

def get_all_presells(db: Session, skip: int = 0, limit: int = 100) -> List[Presell]: # For admin use
    return db.query(Presell).offset(skip).limit(limit).all()

def create_presell(db: Session, presell: PresellCreate, owner_id: Optional[int] = None) -> Presell:
    # Criar um dicionário com os dados do presell, convertendo URLs para string
    presell_data = presell.model_dump()  # Pydantic V2, use presell.dict() for V1
    
    # Converter HttpUrl para string antes de salvar
    presell_data["affiliate_link"] = str(presell_data["affiliate_link"])
    presell_data["product_url"] = str(presell_data["product_url"])
    
    # Adicionar owner_id apenas se não for None
    db_presell = Presell(
        **presell_data,
        owner_id=owner_id,
        status=PresellStatus.RASCUNHO  # Default status on creation
    )
    
    db.add(db_presell)
    db.commit()
    db.refresh(db_presell)
    return db_presell

def update_presell(db: Session, db_presell: Presell, presell_in: PresellUpdate) -> Presell:
    presell_data = presell_in.model_dump(exclude_unset=True) # Pydantic V2, use presell_in.dict(exclude_unset=True) for V1
    for field, value in presell_data.items():
        setattr(db_presell, field, value)
    
    db.add(db_presell)
    db.commit()
    db.refresh(db_presell)
    return db_presell

def delete_presell(db: Session, presell_id: int, owner_id: Optional[int] = None) -> Optional[Presell]:
    db_presell = get_presell(db=db, presell_id=presell_id, owner_id=owner_id)
    if db_presell:
        db.delete(db_presell)
        db.commit()
    return db_presell

# Function to update presell status, public_url, screenshot_path, etc. after generation/deployment
def update_presell_generated_info(
    db: Session, 
    db_presell: Presell, 
    public_url: Optional[str] = None, 
    screenshot_path: Optional[str] = None, 
    generated_html_path: Optional[str] = None,
    status: Optional[PresellStatus] = None
) -> Presell:
    if public_url is not None:
        db_presell.public_url = public_url
    if screenshot_path is not None:
        db_presell.screenshot_path = screenshot_path
    if generated_html_path is not None:
        db_presell.generated_html_path = generated_html_path
    if status is not None:
        db_presell.status = status
    
    db.add(db_presell)
    db.commit()
    db.refresh(db_presell)
    return db_presell

