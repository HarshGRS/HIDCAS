from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Role, Permission, RolePermission, User
from services.rbac import require_permission

router = APIRouter(prefix="/rbac", tags=["RBAC"])

# --- New endpoints for admin UI ---
## Admin endpoints removed to restore original state
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Role, Permission, RolePermission
from services.rbac import require_permission

router = APIRouter(prefix="/rbac", tags=["RBAC"])


@router.post("/grant")
def grant_permission(
    role_name: str,
    permission_name: str,
    db: Session = Depends(get_db),
    user=Depends(require_permission("manage_permissions"))
):
    role = db.query(Role).filter(Role.name == role_name).first()
    permission = db.query(Permission).filter(Permission.name == permission_name).first()

    if not role or not permission:
        raise HTTPException(status_code=404, detail="Role or Permission not found")

    existing = db.query(RolePermission).filter(
        RolePermission.role_id == role.id,
        RolePermission.permission_id == permission.id
    ).first()

    if existing:
        return {"message": "Permission already assigned"}

    new_mapping = RolePermission(
        role_id=role.id,
        permission_id=permission.id
    )

    db.add(new_mapping)
    db.commit()

    return {"message": "Permission granted successfully"}

@router.delete("/remove")
def remove_permission(
    role_name: str,
    permission_name: str,
    db: Session = Depends(get_db),
    user=Depends(require_permission("manage_permissions"))
):
    role = db.query(Role).filter(Role.name == role_name).first()
    permission = db.query(Permission).filter(Permission.name == permission_name).first()

    if not role or not permission:
        raise HTTPException(status_code=404, detail="Role or Permission not found")

    mapping = db.query(RolePermission).filter(
        RolePermission.role_id == role.id,
        RolePermission.permission_id == permission.id
    ).first()

    if not mapping:
        raise HTTPException(status_code=404, detail="Permission not assigned")

    db.delete(mapping)
    db.commit()

    return {"message": "Permission removed successfully"}


from models import Role, Permission, RolePermission, User

@router.put("/assign-role")
def assign_role(
    username: str,
    role_name: str,
    db: Session = Depends(get_db),
    user=Depends(require_permission("manage_permissions"))
):
    target_user = db.query(User).filter(User.username == username).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")

    role = db.query(Role).filter(Role.name == role_name).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")

    target_user.role_id = role.id
    db.commit()

    return {"message": f"{username} ko {role_name} role assign hua"}


@router.get("/roles")
def get_roles(
    db: Session = Depends(get_db),
    user=Depends(require_permission("manage_permissions"))
):
    roles = db.query(Role).all()
    return [{"id": r.id, "name": r.name} for r in roles]


@router.get("/permissions")
def get_permissions(
    db: Session = Depends(get_db),
    user=Depends(require_permission("manage_permissions"))
):
    permissions = db.query(Permission).all()
    return [{"id": p.id, "name": p.name} for p in permissions]


@router.post("/roles")
def create_role(
    role_name: str,
    db: Session = Depends(get_db),
    user=Depends(require_permission("manage_permissions"))
):
    existing = db.query(Role).filter(Role.name == role_name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Role already exists")
    new_role = Role(name=role_name)
    db.add(new_role)
    db.commit()
    db.refresh(new_role)
    return {"message": f"Role '{role_name}' created", "id": new_role.id}


@router.post("/permissions")
def create_permission(
    permission_name: str,
    db: Session = Depends(get_db),
    user=Depends(require_permission("manage_permissions"))
):
    existing = db.query(Permission).filter(Permission.name == permission_name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Permission already exists")
    new_perm = Permission(name=permission_name)
    db.add(new_perm)
    db.commit()
    db.refresh(new_perm)
    return {"message": f"Permission '{permission_name}' created", "id": new_perm.id}


@router.get("/matrix")
def get_matrix(
    db: Session = Depends(get_db),
    user=Depends(require_permission("manage_permissions"))
):
    roles = db.query(Role).all()
    permissions = db.query(Permission).all()
    
    matrix = {}
    for role in roles:
        assigned = [rp.permission_id for rp in role.role_permissions]
        matrix[role.id] = {
            "role_name": role.name,
            "permissions": assigned
        }
    
    return {
        "roles": [{"id": r.id, "name": r.name} for r in roles],
        "permissions": [{"id": p.id, "name": p.name} for p in permissions],
        "matrix": matrix
    }


@router.get("/users")
def get_users(
    db: Session = Depends(get_db),
    user=Depends(require_permission("manage_permissions"))
):
    users = db.query(User).all()
    return [
        {
            "id": u.id,
            "username": u.username,
            "role": u.role.name if u.role else "N/A",
            "role_id": u.role_id
        }
        for u in users
    ]