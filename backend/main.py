from fastapi import FastAPI
from database import engine
import models
import os
from dotenv import load_dotenv

from routes.auth_routes import router as auth_router
from routes.rbac_routes import router as rbac_router
from routes.document_routes import router as document_router
from routes.chat_routes import router as chat_router

load_dotenv()

app = FastAPI()

# CORS configuration - use environment variables for production
from fastapi.middleware.cors import CORSMiddleware
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

if ENVIRONMENT == "development":
    allow_origins = ["*"]
else:
    allow_origins = [
        os.getenv("FRONTEND_URL", "http://localhost:3000"),
        "https://yourdomain.com"  # Update with your actual domain
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

models.Base.metadata.create_all(bind=engine)

# Initialize default roles and permissions
def init_db():
    from database import SessionLocal
    db = SessionLocal()
    
    # Check if roles already exist
    user_role = db.query(models.Role).filter(models.Role.name == "user").first()
    admin_role = db.query(models.Role).filter(models.Role.name == "admin").first()
    
    if not user_role:
        user_role = models.Role(name="user")
        db.add(user_role)
        db.commit()
        db.refresh(user_role)
    
    if not admin_role:
        admin_role = models.Role(name="admin")
        db.add(admin_role)
        db.commit()
        db.refresh(admin_role)
    
    # Add permissions if they don't exist
    permissions_list = [
        "upload_document",
        "view_documents",
        "view_all_documents",
        "delete_document",
        "delete_all_documents",
        "manage_permissions",
        "approve_project"
    ]
    
    for perm_name in permissions_list:
        existing = db.query(models.Permission).filter(models.Permission.name == perm_name).first()
        if not existing:
            perm = models.Permission(name=perm_name)
            db.add(perm)
    
    db.commit()
    
    # Grant permissions to roles
    for perm_name in permissions_list:
        perm = db.query(models.Permission).filter(models.Permission.name == perm_name).first()
        
        # User role gets basic permissions
        if perm_name in ["upload_document", "view_documents", "delete_document"]:
            existing = db.query(models.RolePermission).filter(
                models.RolePermission.role_id == user_role.id,
                models.RolePermission.permission_id == perm.id
            ).first()
            if not existing:
                db.add(models.RolePermission(role_id=user_role.id, permission_id=perm.id))
        
        # Admin role gets all permissions
        existing = db.query(models.RolePermission).filter(
            models.RolePermission.role_id == admin_role.id,
            models.RolePermission.permission_id == perm.id
        ).first()
        if not existing:
            db.add(models.RolePermission(role_id=admin_role.id, permission_id=perm.id))
    
    db.commit()
    db.close()

init_db()

@app.get("/")
def root():
    return {"message": "Backend Running"}

# include routers
app.include_router(auth_router)
app.include_router(rbac_router)
app.include_router(document_router)
app.include_router(chat_router)

# serve the frontend static files (index.html, dashboard etc.)
import os
from fastapi.staticfiles import StaticFiles
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIR = os.path.join(BASE_DIR, "Frontend")
if os.path.isdir(FRONTEND_DIR):
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
else:
    import warnings
    warnings.warn(f"Frontend directory '{FRONTEND_DIR}' does not exist. Static files will not be served.")
