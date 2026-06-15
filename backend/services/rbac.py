from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from database import get_db
from models import User, RolePermission, Permission


def require_permission(permission_name: str):
    # Use HTTPBearer here and import `get_current_user` lazily inside
    # the checker to avoid a circular import with `routes.auth_routes`.
    security = HTTPBearer()

    def permission_checker(
        credentials: HTTPAuthorizationCredentials = Depends(security),
        db: Session = Depends(get_db)
    ):
        # Local import to break circular dependency at module import time
        from routes.auth_routes import get_current_user

        current_user: User = get_current_user(
            credentials=credentials,
            db=db
        )

        permission = db.query(Permission).filter(
            Permission.name == permission_name
        ).first()

        if not permission:
            raise HTTPException(status_code=404, detail="Permission not found")

        role_permission = db.query(RolePermission).filter(
            RolePermission.role_id == current_user.role_id,
            RolePermission.permission_id == permission.id
        ).first()

        if not role_permission:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )

        return current_user

    return permission_checker
