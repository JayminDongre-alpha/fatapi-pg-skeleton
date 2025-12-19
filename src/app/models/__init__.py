"""Models package - Database model definitions.

Import models directly from the database-specific subpackage:
    from app.models.postgres import Base, User, db_manager, get_db
"""

# Optional: convenience re-exports from default backend
from app.models.postgres import Base, DatabaseSessionManager, db_manager, get_db, User

__all__ = ["Base", "DatabaseSessionManager", "db_manager", "get_db", "User"]
