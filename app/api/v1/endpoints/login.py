from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta

from app import crud
from app.schemas.token import Token # Import Token schema directly
from app.schemas.user import User as UserSchema, UserCreate # Import User schema (aliased) and UserCreate
from app.models.user import User as UserModel # Import User model (aliased)
from app.api import deps
from app.core import security
from app.core.config import settings

router = APIRouter()

@router.post("/login/access-token", response_model=Token)
def login_access_token(
    db: Session = Depends(deps.get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
):
    """
    OAuth2 compatible token login, get an access token for future requests.
    """
    user = crud.user.authenticate(
        db,
        email=form_data.username, # OAuth2PasswordRequestForm uses username for the email field
        password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password"
        )
    elif not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data={"sub": user.email, "user_id": user.id, "role": user.role.value if user.role else None}, # Add user_id and role to token
        expires_delta=access_token_expires
    )
    return {
        "access_token": access_token,
        "token_type": "bearer",
    }

@router.post("/login/test-token", response_model=UserSchema)
def test_token(current_user: UserModel = Depends(deps.get_current_active_user)):
    """
    Test access token.
    """
    return current_user

@router.post("/users/", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
def create_user_open(
    *, 
    db: Session = Depends(deps.get_db), 
    user_in: UserCreate
    # current_user: UserModel = Depends(deps.get_current_active_superuser) # To restrict later
):
    """
    Create new user.
    (For MVP, this might be open or we create the first user via script)
    """
    db_user = crud.user.get_user_by_email(db, email=user_in.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The user with this email already exists in the system.",
        )
    created_user = crud.user.create_user(db=db, user_in=user_in) # Ensure crud.user.create_user expects user_in of type UserCreate
    return created_user

