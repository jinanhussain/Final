from builtins import dict, int, len, str
from datetime import timedelta
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Response, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import get_current_user, get_db, get_email_service, require_role
from app.schemas.pagination_schema import EnhancedPagination
from app.schemas.token_schema import TokenResponse
from app.schemas.user_schemas import (
    LoginRequest,
    UserBase,
    UserCreate,
    UserListResponse,
    UserResponse,
    UserUpdate,
    UserProfileUpdate
)
from app.services.user_service import UserService
from app.services.jwt_service import create_access_token
from app.utils.link_generation import create_user_links, generate_pagination_links
from app.dependencies import get_settings
from app.services.email_service import EmailService

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
settings = get_settings()


@router.get("/users/{user_id}", response_model=UserResponse, name="get_user", tags=["User Management"])
async def get_user(
    user_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_role(["ADMIN", "MANAGER"]))
):
    user = await UserService.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse.model_construct(
        id=user.id,
        nickname=user.nickname,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        bio=user.bio,
        github_profile_url=user.github_profile_url,
        linkedin_profile_url=user.linkedin_profile_url,
        role=user.role,
        last_login_at=user.last_login_at,
        created_at=user.created_at,
        updated_at=user.updated_at,
        links=create_user_links(user.id, request)
    )


@router.patch("/users/{user_id}/profile", response_model=UserResponse, name="update_user_profile", tags=["User Management"])
async def update_user_profile(
    user_id: UUID,
    user_update: UserProfileUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    if str(current_user["user_id"]) != str(user_id):
        raise HTTPException(status_code=403, detail="You can only update your own profile.")
    user = await UserService.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    updated_data = user_update.model_dump(exclude_unset=True)
    updated_user = await UserService.update(db, user_id, updated_data)
    return UserResponse.model_construct(**updated_user.dict())


@router.patch("/users/{user_id}/upgrade-professional", response_model=UserResponse, tags=["User Management"])
async def upgrade_user_to_professional(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_role(["ADMIN", "MANAGER"]))
):
    user = await UserService.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_professional = True
    await db.commit()
    await db.refresh(user)
    return UserResponse.model_construct(**user.__dict__)



@router.post("/login/", response_model=TokenResponse, tags=["Login"])
async def login(form_data: OAuth2PasswordRequestForm = Depends(), session: AsyncSession = Depends(get_db)):
    user = await UserService.login_user(session, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.id, "role": user.role}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.delete("/users/{user_id}", status_code=204, tags=["User Management"])
async def delete_user(
    user_id: UUID, db: AsyncSession = Depends(get_db), current_user: dict = Depends(require_role(["ADMIN"]))
):
    success = await UserService.delete(db, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return Response(status_code=204)