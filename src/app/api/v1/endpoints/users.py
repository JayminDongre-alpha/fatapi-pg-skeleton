"""User endpoints using UserService for business logic."""

from fastapi import APIRouter, status

from app.common.dependencies import PaginationParams, UserServiceDep
from app.schemas.user import UserCreate, UserListResponse, UserResponse, UserUpdate

router = APIRouter()


@router.get("", response_model=UserListResponse)
async def list_users(
    service: UserServiceDep,
    pagination: PaginationParams,
) -> UserListResponse:
    """List all users with pagination."""
    users, total = await service.list(
        offset=pagination.offset,
        limit=pagination.limit,
    )

    return UserListResponse(
        items=[UserResponse.model_validate(user) for user in users],
        total=total,
    )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    service: UserServiceDep,
) -> UserResponse:
    """Get a specific user by ID."""
    user = await service.get_by_id(user_id)
    return UserResponse.model_validate(user)


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    service: UserServiceDep,
) -> UserResponse:
    """Create a new user."""
    user = await service.create(user_data)
    return UserResponse.model_validate(user)


@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    service: UserServiceDep,
) -> UserResponse:
    """Update an existing user."""
    user = await service.update(user_id, user_data)
    return UserResponse.model_validate(user)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    service: UserServiceDep,
) -> None:
    """Delete a user."""
    await service.delete(user_id)
