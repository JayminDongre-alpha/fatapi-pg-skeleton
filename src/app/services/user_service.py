"""User service for user-related business logic."""

from sqlalchemy import func, select

from app.common.exceptions import ConflictException, NotFoundException
from app.models.postgres.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.services.base import BaseService


class UserService(BaseService):
    """Service for user-related operations."""

    async def get_by_id(self, user_id: int) -> User:
        """Get a user by ID.

        Args:
            user_id: The user's ID

        Returns:
            The user object

        Raises:
            NotFoundException: If user is not found
        """
        query = select(User).where(User.id == user_id)
        result = await self.db.execute(query)
        user = result.scalar_one_or_none()

        if not user:
            raise NotFoundException("User")

        return user

    async def get_by_email(self, email: str) -> User | None:
        """Get a user by email.

        Args:
            email: The user's email address

        Returns:
            The user object or None if not found
        """
        query = select(User).where(User.email == email)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def list(
        self, offset: int = 0, limit: int = 10
    ) -> tuple[list[User], int]:
        """List users with pagination.

        Args:
            offset: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            Tuple of (list of users, total count)
        """
        # Get total count
        count_query = select(func.count()).select_from(User)
        total = (await self.db.execute(count_query)).scalar() or 0

        # Get paginated users
        query = select(User).offset(offset).limit(limit)
        result = await self.db.execute(query)
        users = list(result.scalars().all())

        return users, total

    async def create(self, data: UserCreate) -> User:
        """Create a new user.

        Args:
            data: User creation data

        Returns:
            The created user

        Raises:
            ConflictException: If email already exists
        """
        # Check if email already exists
        existing = await self.get_by_email(data.email)
        if existing:
            raise ConflictException("User with this email already exists")

        # Create user (password should be hashed in production)
        user = User(
            email=data.email,
            hashed_password=data.password,  # TODO: Hash password
            full_name=data.full_name,
        )
        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)

        return user

    async def update(self, user_id: int, data: UserUpdate) -> User:
        """Update an existing user.

        Args:
            user_id: The user's ID
            data: User update data

        Returns:
            The updated user

        Raises:
            NotFoundException: If user is not found
        """
        user = await self.get_by_id(user_id)

        # Update fields
        update_data = data.model_dump(exclude_unset=True)
        if "password" in update_data:
            update_data["hashed_password"] = update_data.pop("password")  # TODO: Hash

        for field, value in update_data.items():
            setattr(user, field, value)

        await self.db.flush()
        await self.db.refresh(user)

        return user

    async def delete(self, user_id: int) -> None:
        """Delete a user.

        Args:
            user_id: The user's ID

        Raises:
            NotFoundException: If user is not found
        """
        user = await self.get_by_id(user_id)
        await self.db.delete(user)
