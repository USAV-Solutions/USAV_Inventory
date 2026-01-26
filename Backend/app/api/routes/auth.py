"""
Authentication API endpoints.
Handles login, token generation, and user management.
"""
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import AdminUser, CurrentUser
from app.core.database import get_db
from app.core.security import create_access_token, get_password_hash, verify_password
from app.models import User, UserRole
from app.repositories.user import UserRepository
from app.schemas import (
    PaginatedResponse,
    PasswordChange,
    Token,
    UserCreate,
    UserResponse,
    UserUpdate,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


# ============================================================================
# AUTHENTICATION ENDPOINTS
# ============================================================================

@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: AsyncSession = Depends(get_db),
):
    """
    OAuth2 compatible token login.
    
    Authenticate with username and password, receive JWT access token.
    """
    repo = UserRepository(db)
    user = await repo.get_by_username(form_data.username)
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled",
        )
    
    # Update last login timestamp
    user.last_login = datetime.now()
    await db.flush()
    
    # Create access token
    access_token = create_access_token(
        subject=user.id,
        role=user.role.value,
        extra_data={"username": user.username},
    )
    
    return Token(access_token=access_token, token_type="bearer")


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: CurrentUser,
):
    """Get current authenticated user's information."""
    return UserResponse.model_validate(current_user)


@router.post("/me/change-password", status_code=status.HTTP_204_NO_CONTENT)
async def change_own_password(
    password_data: PasswordChange,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Change current user's password."""
    if not verify_password(password_data.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect",
        )
    
    current_user.hashed_password = get_password_hash(password_data.new_password)
    await db.flush()


# ============================================================================
# USER MANAGEMENT ENDPOINTS (Admin only)
# ============================================================================

@router.get("/users", response_model=PaginatedResponse)
async def list_users(
    current_user: AdminUser,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=1000)] = 100,
    role: Annotated[UserRole | None, Query(description="Filter by role")] = None,
    is_active: Annotated[bool | None, Query(description="Filter by active status")] = None,
    db: AsyncSession = Depends(get_db),
):
    """List all users (Admin only)."""
    repo = UserRepository(db)
    
    filters = {}
    if role is not None:
        filters["role"] = role
    if is_active is not None:
        filters["is_active"] = is_active
    
    items = await repo.get_multi(skip=skip, limit=limit, filters=filters, order_by="id")
    total = await repo.count(filters=filters)
    
    return PaginatedResponse(
        total=total,
        skip=skip,
        limit=limit,
        items=[UserResponse.model_validate(u) for u in items]
    )


@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    current_user: AdminUser,
    db: AsyncSession = Depends(get_db),
):
    """Create a new user (Admin only). Roles are assigned by admins."""
    repo = UserRepository(db)
    
    # Check for existing username
    if await repo.username_exists(user_data.username):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Username '{user_data.username}' is already taken",
        )
    
    # Create user with hashed password
    user_dict = user_data.model_dump(exclude={"password"})
    user_dict["hashed_password"] = get_password_hash(user_data.password)
    
    user = await repo.create(user_dict)
    return UserResponse.model_validate(user)


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    current_user: AdminUser,
    db: AsyncSession = Depends(get_db),
):
    """Get a specific user by ID (Admin only)."""
    repo = UserRepository(db)
    user = await repo.get(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {user_id} not found",
        )
    
    return UserResponse.model_validate(user)


@router.patch("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    current_user: AdminUser,
    db: AsyncSession = Depends(get_db),
):
    """Update a user (Admin only)."""
    repo = UserRepository(db)
    user = await repo.get(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {user_id} not found",
        )
    
    update_dict = user_data.model_dump(exclude_unset=True, exclude={"password"})
    
    # Handle password update separately
    if user_data.password:
        update_dict["hashed_password"] = get_password_hash(user_data.password)
    
    if update_dict:
        user = await repo.update(user, update_dict)
    
    return UserResponse.model_validate(user)


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    current_user: AdminUser,
    db: AsyncSession = Depends(get_db),
):
    """Delete a user (Admin only)."""
    repo = UserRepository(db)
    
    # Prevent self-deletion
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account",
        )
    
    deleted = await repo.delete(user_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {user_id} not found",
        )


@router.post("/users/{user_id}/deactivate", response_model=UserResponse)
async def deactivate_user(
    user_id: int,
    current_user: AdminUser,
    db: AsyncSession = Depends(get_db),
):
    """Deactivate a user account (Admin only)."""
    repo = UserRepository(db)
    user = await repo.get(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {user_id} not found",
        )
    
    # Prevent self-deactivation
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot deactivate your own account",
        )
    
    user = await repo.update(user, {"is_active": False})
    return UserResponse.model_validate(user)


@router.post("/users/{user_id}/activate", response_model=UserResponse)
async def activate_user(
    user_id: int,
    current_user: AdminUser,
    db: AsyncSession = Depends(get_db),
):
    """Activate a user account (Admin only)."""
    repo = UserRepository(db)
    user = await repo.get(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {user_id} not found",
        )
    
    user = await repo.update(user, {"is_active": True})
    return UserResponse.model_validate(user)
