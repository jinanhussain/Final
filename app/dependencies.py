from builtins import Exception, dict, str
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import Database
from app.utils.template_manager import TemplateManager
from app.services.email_service import EmailService
from app.services.jwt_service import decode_token
from settings.config import Settings

# Settings Dependency
def get_settings() -> Settings:
    """Return application settings."""
    return Settings()

# Email Service Dependency
def get_email_service() -> EmailService:
    """Provide the EmailService instance."""
    template_manager = TemplateManager()
    return EmailService(template_manager=template_manager)

# Database Session Dependency
async def get_db() -> AsyncSession:
    """
    Dependency that provides an async database session for each request.
    Ensures sessions are properly closed even in case of exceptions.
    """
    async_session_factory = Database.get_session_factory()
    async with async_session_factory() as session:
        try:
            yield session
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Database connection error: {str(e)}"
            )

# OAuth2 Token Scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

# Current User Dependency
def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Extract the current user information (id and role) from the JWT token.
    """
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_token(token)  # Ensure this decodes the JWT correctly
    if not payload:
        raise credentials_exception

    user_id: str = payload.get("sub")  # 'sub' is typically used for user id
    user_role: str = payload.get("role")

    if not user_id or not user_role:
        raise credentials_exception

    return {"user_id": user_id, "role": user_role}

# Role-Based Access Control Dependency
def require_role(allowed_roles: list[str]):
    """
    Ensure the current user has one of the allowed roles.
    Example usage:
        @app.get("/admin", dependencies=[Depends(require_role(["admin"]))])
    """
    def role_checker(current_user: dict = Depends(get_current_user)):
        if current_user["role"] not in allowed_roles:
            raise HTTPException(
                status_code=403,
                detail="Operation not permitted. Insufficient role privileges.",
            )
        return current_user

    return role_checker
