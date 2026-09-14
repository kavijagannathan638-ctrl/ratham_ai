from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
import jwt
from app.core.database import get_db
from app.core.security import decode_token
from app.models.user import User, UserRole

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)

def get_current_user(
    db: Session = Depends(get_db),
    token: Optional[str] = Depends(oauth2_scheme)
) -> Optional[User]:
    if not token:
        # For public/demo mode fallback when auth is bypassed or missing
        user = db.query(User).filter(User.email == "demo@ratham.ai").first()
        if user:
            return user
        # Return default synthetic coordinator user if DB not seeded yet
        return User(id=1, email="coordinator@ratham.ai", name="Operational Coordinator", role=UserRole.COORDINATOR)
    
    try:
        payload = decode_token(token)
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")
        user = db.query(User).filter(User.id == int(user_id)).first()
        if not user or not user.is_active:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User disabled or not found")
        return user
    except (jwt.PyJWTError, ValueError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired authentication token")

def require_role(roles: list[UserRole]):
    def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role not in roles and current_user.role != UserRole.SUPER_ADMIN:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied for user role")
        return current_user
    return role_checker
