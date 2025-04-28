from fastapi import APIRouter, HTTPException, Depends, Response, Cookie
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from schemas.mysql import user
from models.mysql_models import UserMySql
from config import get_db, SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
from typing import Optional
from pydantic import BaseModel

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme for token authentication - used for Swagger UI
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

router = APIRouter(prefix="/auth")


# Token model
class Token(BaseModel):
    access_token: str
    token_type: str


# Token data model
class TokenData(BaseModel):
    username: Optional[str] = None


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def authenticate_user(db: Session, username: str, password: str):
    user_db = db.query(UserMySql).filter(UserMySql.username == username).first()
    if not user_db or not verify_password(password, user_db.hashed_password):
        return False
    return user_db


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta
        if expires_delta
        else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# Single function to validate JWT token (from either cookie or Bearer header)
def get_token_data(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            return None
        return TokenData(username=username)
    except JWTError:
        return None


# Dependency that checks both cookie and header
def get_current_user(
    db: Session = Depends(get_db),
    token: Optional[str] = Depends(oauth2_scheme),
    session_token: Optional[str] = Cookie(None),
):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Not authenticated. Please log in.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Try to get token from header first, then from cookie
    auth_token = token or session_token
    if not auth_token:
        raise credentials_exception

    token_data = get_token_data(auth_token)
    if token_data is None:
        raise credentials_exception

    user_db = (
        db.query(UserMySql).filter(UserMySql.username == token_data.username).first()
    )
    if user_db is None:
        raise credentials_exception

    return user_db


def get_admin_user(current_user: UserMySql = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required.")
    return current_user


@router.post("/register", response_model=user.UserRead)
def register(user_create: user.UserCreate, db: Session = Depends(get_db)):
    # Check if username or email already exists
    db_user = (
        db.query(UserMySql)
        .filter(
            (UserMySql.username == user_create.username)
            | (UserMySql.email == user_create.email)
        )
        .first()
    )

    if db_user:
        raise HTTPException(
            status_code=400, detail="Username or email already registered"
        )

    # Create new user with hashed password
    db_user = UserMySql(
        username=user_create.username,
        email=user_create.email,
        hashed_password=get_password_hash(user_create.password),
    )

    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Registration failed")


@router.post("/login", response_model=Token)
def login(
    response: Response,  # Add response parameter
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user_db = authenticate_user(db, form_data.username, form_data.password)
    if not user_db:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user_db.username}, expires_delta=access_token_expires
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

    # Return token in response body as well (for API clients)
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/logout")
def logout(response: Response):
    response.delete_cookie(key="session_token")
    return {"message": "Logged out successfully"}


@router.get("/me", response_model=user.UserRead)
def get_current_user_profile(current_user: UserMySql = Depends(get_current_user)):
    return current_user
