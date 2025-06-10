from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from typing import List, Any, Optional
import asyncio
import os
from fastapi.responses import HTMLResponse, FileResponse
import pathlib

from app import crud
from app.models.presell import Presell
from app.schemas.presell import Presell as PresellSchema, PresellCreate, PresellUpdate, PresellStatus
from app.api import deps
from app.services.presell_processor import process_presell_creation
from app.core.config import settings

router = APIRouter()

@router.post("/", response_model=PresellSchema, status_code=status.HTTP_201_CREATED)
async def create_presell(
    *, 
    db: Session = Depends(deps.get_db),
    presell_in: PresellCreate
) -> Any:
    """
    Create new presell.
    """
    # Check if slug already exists
    existing_presell = db.query(Presell).filter(Presell.slug == presell_in.slug).first()
    if existing_presell:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"The slug '{presell_in.slug}' is already in use. Please choose a different one."
        )

    # Create presell in database first to get ID
    db_presell = crud.presell.create_presell(db=db, presell=presell_in, owner_id=None)
    
    # Process presell creation (screenshot capture and HTML generation)
    result = await process_presell_creation(
        presell_id=db_presell.id,
        presell_type=db_presell.presell_type,
        affiliate_link=str(db_presell.affiliate_link),
        product_url=str(db_presell.product_url),
        language_code=db_presell.language_code,
        slug=db_presell.slug,
        custom_background_image_url=db_presell.custom_background_image_url # Pass custom URL
    )
    
    # Update presell with generated assets and set status to PUBLICADA if successful
    if result["screenshot_path"] and result["generated_html_path"] and result["public_url"]:
        db_presell = crud.presell.update_presell_generated_info(
            db=db, 
            db_presell=db_presell, 
            screenshot_path=result["screenshot_path"],
            generated_html_path=result["generated_html_path"],
            public_url=result["public_url"],
            status=PresellStatus.PUBLICADA
        )
    else:
        # If something failed, keep as draft
        db_presell = crud.presell.update_presell_generated_info(
            db=db, 
            db_presell=db_presell, 
            screenshot_path=result.get("screenshot_path"),
            generated_html_path=result.get("generated_html_path"),
            public_url=result.get("public_url"),
            status=PresellStatus.RASCUNHO
        )

    return db_presell

@router.get("/", response_model=List[PresellSchema])
def read_presells(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100
) -> Any:
    """
    Retrieve all presells.
    """
    presells = crud.presell.get_all_presells(db, skip=skip, limit=limit)
    return presells

@router.get("/{presell_id}", response_model=PresellSchema)
def read_presell(
    *, 
    db: Session = Depends(deps.get_db),
    presell_id: int
) -> Any:
    """
    Get presell by ID.
    """
    presell = crud.presell.get_presell(db=db, presell_id=presell_id, owner_id=None)
    if not presell:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Presell not found")
    return presell

@router.get("/view/{slug}", response_class=HTMLResponse)
def view_presell_by_slug(
    *,
    db: Session = Depends(deps.get_db),
    slug: str
) -> Any:
    """
    View presell by slug - returns the generated HTML directly.
    This endpoint is used for public access to the presell page.
    """
    # Get presell by slug
    presell = crud.presell.get_presell_by_slug(db=db, slug=slug)
    if not presell:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Presell not found")
    
    # Check if presell is published and has a generated HTML file
    if presell.status != PresellStatus.PUBLICADA or not presell.generated_html_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Presell is not published or HTML not generated"
        )
    
    # Check if the HTML file exists
    html_path = pathlib.Path(presell.generated_html_path)
    if not html_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Presell HTML file not found"
        )
    
    # Read the HTML content
    with open(html_path, "r", encoding="utf-8") as f:
        html_content = f.read()
    
    # Return the HTML content
    return HTMLResponse(content=html_content, status_code=200)

@router.put("/{presell_id}", response_model=PresellSchema)
async def update_presell(
    *, 
    db: Session = Depends(deps.get_db),
    presell_id: int,
    presell_in: PresellUpdate
) -> Any:
    """
    Update a presell.
    """
    db_presell = crud.presell.get_presell(db=db, presell_id=presell_id, owner_id=None)
    if not db_presell:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Presell not found")
    
    # Check if slug is being changed and if it's already in use
    if presell_in.slug and presell_in.slug != db_presell.slug:
        existing_presell = db.query(Presell).filter(
            Presell.slug == presell_in.slug, 
            Presell.id != presell_id
        ).first()
        if existing_presell:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"The slug '{presell_in.slug}' is already in use. Please choose a different one."
            )
    
    # Update presell in database
    updated_presell = crud.presell.update_presell(db=db, db_presell=db_presell, presell_in=presell_in)
    
    # Check if we need to regenerate assets (if product_url, affiliate_link, presell_type or language_code changed)
    needs_regeneration = (
        (presell_in.product_url and presell_in.product_url != db_presell.product_url) or
        (presell_in.affiliate_link and presell_in.affiliate_link != db_presell.affiliate_link) or
        (presell_in.presell_type and presell_in.presell_type != db_presell.presell_type) or
        (presell_in.language_code and presell_in.language_code != db_presell.language_code)
    )
    
    if needs_regeneration:
        # Process presell creation (screenshot capture and HTML generation)
        result = await process_presell_creation(
            presell_id=updated_presell.id,
            presell_type=updated_presell.presell_type,
            affiliate_link=str(updated_presell.affiliate_link),
            product_url=str(updated_presell.product_url),
            language_code=updated_presell.language_code,
            slug=updated_presell.slug
        )
        
        # Update presell with generated assets
        if result["screenshot_path"] and result["generated_html_path"] and result["public_url"]:
            updated_presell = crud.presell.update_presell_generated_info(
                db=db, 
                db_presell=updated_presell, 
                screenshot_path=result["screenshot_path"],
                generated_html_path=result["generated_html_path"],
                public_url=result["public_url"],
                status=PresellStatus.PUBLICADA
            )
    
    return updated_presell

@router.delete("/{presell_id}", response_model=PresellSchema)
def delete_presell(
    *, 
    db: Session = Depends(deps.get_db),
    presell_id: int
) -> Any:
    """
    Delete a presell.
    """
    db_presell = crud.presell.get_presell(db=db, presell_id=presell_id, owner_id=None)
    if not db_presell:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Presell not found")
    
    # Delete associated files
    if db_presell.screenshot_path and os.path.exists(db_presell.screenshot_path):
        try:
            os.remove(db_presell.screenshot_path)
        except OSError as e:
            print(f"Error deleting screenshot file {db_presell.screenshot_path}: {e}")
    
    if db_presell.generated_html_path and os.path.exists(db_presell.generated_html_path):
        try:
            os.remove(db_presell.generated_html_path)
        except OSError as e:
            print(f"Error deleting HTML file {db_presell.generated_html_path}: {e}")
    
    # Delete from database
    deleted_presell = crud.presell.delete_presell(db=db, presell_id=presell_id, owner_id=None)
    return deleted_presell
