from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import models
from auth import hash_password, verify_password, create_access_token, verify_token
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from services.rbac import require_permission
from pydantic import BaseModel


router = APIRouter()

security = HTTPBearer()

# Pydantic models for request/response
class LoginRequest(BaseModel):
    username: str
    password: str

class RegisterRequest(BaseModel):
    username: str
    password: str


# 🔐 Get Current User
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    token = credentials.credentials
    payload = verify_token(token)
    username = payload.get("sub")

    if username is None:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(models.User).filter(models.User.username == username).first()

    if user is None:
        raise HTTPException(status_code=401, detail="User not found")

    return user


# 📝 Register
@router.post("/register")
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    username = request.username
    password = request.password
    
    existing_user = db.query(models.User).filter(
        models.User.username == username
    ).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")

    # Default role "user" assigned 
    default_role = db.query(models.Role).filter(
        models.Role.name == "user"
    ).first()

    if not default_role:
        raise HTTPException(
            status_code=500, 
            detail="Default role not configured. Contact admin."
        )

    new_user = models.User(
        username=username,
        hashed_password=hash_password(password),
        role_id=default_role.id
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "User registered successfully"}


# 🔐 Login
@router.post("/login")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    username = request.username
    password = request.password

    user = db.query(models.User).filter(models.User.username == username).first()

    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    token = create_access_token(
        data={"sub": user.username}
    )

    return {"access_token": token, "token_type": "bearer"}


@router.get("/protected")
def protected(current_user = Depends(get_current_user)):
    return {"message": f"Hello {current_user.username}"}

@router.get("/admin-only")
def admin_only_route(
    current_user = Depends(require_permission("approve_project"))
):
    return {"message": f"Welcome Admin {current_user.username}"}

# Get current logged-in user info
@router.get("/me")
def get_current_user_info(current_user = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "username": current_user.username,
        "role": current_user.role.name if current_user.role else None,
        "permissions": [
            rp.permission.name for rp in current_user.role.role_permissions
        ] if current_user.role else []
    }
