from fastapi import (
    APIRouter,
    FastAPI,
    HTTPException,
    Depends,
    Response,
    Cookie,
    Request,
)
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from schemas.mysql import user
from config import get_db, SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
import os
from pydantic import BaseModel

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

router = APIRouter(prefix="/auth")


# Token model
class Token(BaseModel):
    access_token: str
    token_type: str


# Token data model
class TokenData(BaseModel):
    username: Optional[str] = None


# Helper function to verify password
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


# Helper function to hash password
def get_password_hash(password):
    return pwd_context.hash(password)


# Helper function to authenticate user
def authenticate_user(db: Session, username: str, password: str):
    user_db = db.query(user.User).filter(user.User.username == username).first()
    if not user_db:
        return False
    if not verify_password(password, user_db.hashed_password):
        return False
    return user_db


# Helper function to create access token
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# Get current user from token
async def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user_db = (
        db.query(user.User).filter(user.User.username == token_data.username).first()
    )
    if user_db is None:
        raise credentials_exception
    return user_db


# Register endpoint
@router.post("/register", response_model=user.UserRead)
def register(user_create: user.UserCreate, db: Session = Depends(get_db)):
    # Check if username or email already exists
    db_user = (
        db.query(user.User)
        .filter(
            (user.User.username == user_create.username)
            | (user.User.email == user_create.email)
        )
        .first()
    )

    if db_user:
        raise HTTPException(
            status_code=400, detail="Username or email already registered"
        )

    # Create new user with hashed password
    hashed_password = get_password_hash(user_create.password)
    db_user = user.User(
        username=user_create.username,
        email=user_create.email,
        hashed_password=hashed_password,
    )

    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Registration failed")


# Login endpoint
@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    user_db = authenticate_user(db, form_data.username, form_data.password)
    if not user_db:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create access token with expiration time
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user_db.username}, expires_delta=access_token_expires
    )

    # Create response with token in cookies
    response = JSONResponse(
        content={"access_token": access_token, "token_type": "bearer"}
    )

    # Set secure httpOnly cookie
    response.set_cookie(
        key="session_token",
        value=access_token,
        httponly=True,
        secure=True,  # Set to False in development
        samesite="lax",
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )

    return response


# Logout endpoint
@router.post("/logout")
async def logout(response: Response):
    response = JSONResponse(content={"message": "Logged out successfully"})
    # Clear the session cookie
    response.delete_cookie(key="session_token")
    return response


# Get current user profile
@router.get("/me", response_model=user.UserRead)
async def get_current_user_profile(
    current_user: user.UserRead = Depends(get_current_user),
):
    return current_user


# Session validation from cookie
async def get_current_user_from_cookie(
    session_token: Optional[str] = Cookie(None), db: Session = Depends(get_db)
):
    if not session_token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(session_token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception

    user_db = (
        db.query(user.User).filter(user.User.username == token_data.username).first()
    )
    if user_db is None:
        raise credentials_exception
    return user_db
