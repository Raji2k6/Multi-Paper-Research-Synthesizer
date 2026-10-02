from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_db
from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse, UserResponse


router = APIRouter(prefix="/auth", tags=["Authentication"])


def _token_response(user: User) -> TokenResponse:
    return TokenResponse(
        access_token=create_access_token(user.id),
        user=UserResponse(id=user.id, email=user.email, name=user.name),
    )


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    if db.query(User.id).filter(User.email == request.email).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists.",
        )

    user = User(
        id=str(uuid4()),
        email=request.email,
        name=request.name,
        password_hash=hash_password(request.password),
    )
    access_token = create_access_token(user.id)
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists.",
        ) from None
    db.refresh(user)
    return TokenResponse(
        access_token=access_token,
        user=UserResponse(id=user.id, email=user.email, name=user.name),
    )


@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email).first()
    if user is None or not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email or password is incorrect.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return _token_response(user)


@router.get("/me", response_model=UserResponse)
def get_me(user: User = Depends(get_current_user)):
    return UserResponse(id=user.id, email=user.email, name=user.name)
