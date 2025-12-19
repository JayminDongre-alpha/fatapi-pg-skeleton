"""Sample user endpoints."""

from fastapi import APIRouter, status
from sqlalchemy import func, select

from app.common.dependencies import DBSession, PaginationParams
from app.common.exceptions import ConflictException, NotFoundException
from app.models.postgres.user import User
from app.schemas.user import UserCreate, UserListResponse, UserResponse, UserUpdate

router = APIRouter()


@router.get("", response_model=UserListResponse)
async def list_users(
    db: DBSession,
    pagination: PaginationParams,
) -> UserListResponse:
    """List all users with pagination."""
    # Get total count
    count_query = select(func.count()).select_from(User)
    total = (await db.execute(count_query)).scalar() or 0

    # Get paginated users
    query = select(User).offset(pagination.offset).limit(pagination.limit)
    result = await db.execute(query)
    users = result.scalars().all()

    return UserListResponse(
        items=[UserResponse.model_validate(user) for user in users],
        total=total,
    )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: DBSession,
) -> UserResponse:
    """Get a specific user by ID."""
    query = select(User).where(User.id == user_id)
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if not user:
        raise NotFoundException("User")

    return UserResponse.model_validate(user)


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    db: DBSession,
) -> UserResponse:
    """Create a new user."""
    # Check if email already exists
    query = select(User).where(User.email == user_data.email)
    result = await db.execute(query)
    if result.scalar_one_or_none():
        raise ConflictException("User with this email already exists")

    # Create user (password should be hashed in production)
    user = User(
        email=user_data.email,
        hashed_password=user_data.password,  # TODO: Hash password
        full_name=user_data.full_name,
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)

    return UserResponse.model_validate(user)


@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: DBSession,
) -> UserResponse:
    """Update an existing user."""
    query = select(User).where(User.id == user_id)
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if not user:
        raise NotFoundException("User")

    # Update fields
    update_data = user_data.model_dump(exclude_unset=True)
    if "password" in update_data:
        update_data["hashed_password"] = update_data.pop("password")  # TODO: Hash

    for field, value in update_data.items():
        setattr(user, field, value)

    await db.flush()
    await db.refresh(user)

    return UserResponse.model_validate(user)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    db: DBSession,
) -> None:
    """Delete a user."""
    query = select(User).where(User.id == user_id)
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if not user:
        raise NotFoundException("User")

    await db.delete(user)
