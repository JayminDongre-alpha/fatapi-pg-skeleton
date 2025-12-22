# FastAPI Skeleton

A production-ready FastAPI project skeleton with async SQLAlchemy, structured JSON logging, CLI tools, and PostgreSQL support.

## Features

- **FastAPI** with async/await support
- **SQLAlchemy 2.0** async ORM with PostgreSQL
- **Pydantic v2** for validation and settings
- **Alembic** for database migrations
- **Typer CLI** for command-line tools
- **Structured JSON Logging** with rotating file handlers
- **Request/Response Middleware** with timing and request IDs
- **Versioned API** structure (`/api/v1/`)
- **Layered Architecture** with services and providers separation

## Project Structure

```
fastapi-skeleton/
├── src/app/
│   ├── main.py                 # FastAPI app entry point
│   ├── core/
│   │   ├── config.py           # Settings (pydantic-settings)
│   │   ├── logging_config.py   # JSON rotating logger
│   │   ├── middleware.py       # Request/Response logging
│   │   ├── lifespan.py         # Startup/shutdown events
│   │   └── router.py           # Root router mapper
│   ├── services/               # Business logic layer
│   │   ├── base.py             # BaseService class
│   │   └── user_service.py     # UserService (CRUD operations)
│   ├── providers/              # Third-party integrations
│   │   ├── base.py             # BaseProvider abstract class
│   │   └── email_provider.py   # Email/SMTP provider
│   ├── models/
│   │   └── postgres/
│   │       ├── base.py         # Base model (id, timestamps)
│   │       ├── database.py     # Async DB session manager
│   │       └── user.py         # Sample User model
│   ├── api/v1/endpoints/       # API endpoints (thin handlers)
│   ├── schemas/                # Pydantic schemas
│   └── common/                 # Helpers, exceptions, dependencies
├── cli/                        # CLI commands
├── tests/                      # Test suite
├── alembic/                    # Database migrations
└── logs/                       # Log files
```

## Architecture

This project follows a **layered architecture** pattern:

```
HTTP Request → Endpoint → Service → Model → Database
                             ↓
                         Provider (for 3rd party APIs)
```

| Layer | Purpose | Example |
|-------|---------|---------|
| **Endpoints** | Thin HTTP handlers, routing, response formatting | `api/v1/endpoints/users.py` |
| **Services** | Business logic, validation, orchestration | `services/user_service.py` |
| **Models** | Database ORM, data persistence | `models/postgres/user.py` |
| **Providers** | Third-party integrations (email, payment, etc.) | `providers/email_provider.py` |

### Services

Services contain all business logic. Endpoints should not access models directly.

```python
# In endpoint (thin handler)
@router.get("/{user_id}")
async def get_user(user_id: int, service: UserServiceDep) -> UserResponse:
    user = await service.get_by_id(user_id)
    return UserResponse.model_validate(user)
```

```python
# In service (business logic)
class UserService(BaseService):
    async def get_by_id(self, user_id: int) -> User:
        query = select(User).where(User.id == user_id)
        result = await self.db.execute(query)
        user = result.scalar_one_or_none()
        if not user:
            raise NotFoundException("User")
        return user
```

### Providers

Providers handle third-party integrations. Services can use providers for external operations.

```python
# Example: Service using a provider
class UserService(BaseService):
    def __init__(self, db: AsyncSession, email: EmailProvider):
        super().__init__(db)
        self.email = email

    async def create(self, data: UserCreate) -> User:
        user = await self._create_user(data)
        await self.email.send_email(
            to=user.email,
            subject="Welcome!",
            body="Thanks for signing up."
        )
        return user
```

To enable email, add SMTP settings to `.env`:
```env
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USER=your-username
SMTP_PASSWORD=your-password
SMTP_FROM_EMAIL=noreply@example.com
```

## Installation

### Prerequisites
- Python 3.11+
- PostgreSQL

### Setup

```bash
# Clone and navigate to project
cd fastapi-skeleton

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Edit .env with your database credentials
```

## Configuration

Edit `.env` file:

```env
# Application
APP_NAME=FastAPI Skeleton
APP_VERSION=1.0.0
DEBUG=true
ENVIRONMENT=development

# Server
HOST=0.0.0.0
PORT=8000

# Database
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/fastapi_skeleton
DB_POOL_SIZE=5
DB_MAX_OVERFLOW=10

# Logging
LOG_LEVEL=INFO
LOG_DIR=logs
LOG_MAX_BYTES=10485760
LOG_BACKUP_COUNT=5
```

## Running the Server

### Using CLI
```bash
python cli/main.py server run --reload
```

### Using Uvicorn directly
```bash
cd src && uvicorn app.main:app --reload
```

### Server Options
```bash
python cli/main.py server run --help

Options:
  -h, --host TEXT      Host to bind [default: 0.0.0.0]
  -p, --port INTEGER   Port to bind [default: 8000]
  -r, --reload         Enable auto-reload
  -w, --workers INTEGER Number of workers [default: 1]
```

## Database Migrations

This project uses Alembic for database migrations. For comprehensive documentation including production scenarios, troubleshooting, and best practices, see **[alembic-readme.md](alembic-readme.md)**.

### Quick Start (Fresh Database)

```bash
# 1. Create the database
createdb fastapi_skeleton

# 2. Stamp database to initialize Alembic tracking
python3 cli/main.py db stamp head

# 3. Generate initial migration
python3 cli/main.py db migrate --message "Initial migration"

# 4. Apply the migration
python3 cli/main.py db migrate

# 5. (Optional) Seed with sample data
python3 cli/main.py db seed
```

### Common Migration Commands

| Command | Description |
|---------|-------------|
| `db migrate` | Apply all pending migrations |
| `db migrate -m "message"` | Generate new migration |
| `db upgrade [revision]` | Upgrade to specific revision (default: head) |
| `db downgrade <revision>` | Downgrade to specific revision |
| `db rollback -s 1` | Rollback last migration |
| `db stamp head` | Sync Alembic tracking (fixes common errors) |
| `db current` | Show current revision |
| `db history` | Show migration history |
| `db reset` | Drop all tables and recreate |

### Troubleshooting

**"Target database is not up to date"** error:
```bash
python3 cli/main.py db stamp head
# Then retry your command
```

For more scenarios (production deployments, rollbacks, data migrations), see [alembic-readme.md](alembic-readme.md).

## CLI Commands

### Server Commands
```bash
python cli/main.py server run       # Run server
python cli/main.py server shell     # Interactive Python shell
python cli/main.py server routes    # List all routes
```

### Database Commands
```bash
python cli/main.py db migrate                    # Apply migrations
python cli/main.py db migrate -m "add users"    # Create new migration
python cli/main.py db upgrade                   # Upgrade to head
python cli/main.py db upgrade abc123            # Upgrade to specific revision
python cli/main.py db downgrade -1              # Downgrade 1 step
python cli/main.py db downgrade base            # Downgrade to empty database
python cli/main.py db rollback -s 1             # Rollback 1 migration
python cli/main.py db stamp head                # Stamp database
python cli/main.py db seed                      # Seed initial data
python cli/main.py db reset                     # Reset database
python cli/main.py db current                   # Show current revision
python cli/main.py db history                   # Show migration history
```

### General Commands
```bash
python cli/main.py version    # Show version
python cli/main.py info       # Show configuration
```

## API Endpoints

### Health Check
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/health` | Basic health check |
| GET | `/api/v1/health/db` | Database health check |
| GET | `/api/v1/health/ready` | Readiness check |

### Users (Sample CRUD)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/users` | List users (paginated) |
| GET | `/api/v1/users/{id}` | Get user by ID |
| POST | `/api/v1/users` | Create user |
| PATCH | `/api/v1/users/{id}` | Update user |
| DELETE | `/api/v1/users/{id}` | Delete user |

### API Documentation
- Swagger UI: `http://localhost:8000/docs` (debug mode only)
- ReDoc: `http://localhost:8000/redoc` (debug mode only)

## Logging

Logs are written in JSON format to rotating files:

| Log File | Purpose |
|----------|---------|
| `logs/access.log` | API request/response logs |
| `logs/error.log` | Error logs with stack traces |
| `logs/app.log` | General application logs |

### Log Format Example
```json
{
  "timestamp": "2025-01-15T10:30:00+00:00",
  "level": "INFO",
  "logger": "app.access",
  "message": "Request completed",
  "module": "middleware",
  "function": "dispatch",
  "line": 45,
  "extra": {
    "request_id": "abc-123",
    "client_ip": "127.0.0.1",
    "method": "GET",
    "url": "/api/v1/health",
    "status_code": 200,
    "duration_ms": 12.5
  }
}
```

## Testing

```bash
# Install dev dependencies
pip install pytest pytest-asyncio pytest-cov aiosqlite

# Run tests
pytest

# Run with coverage
pytest --cov=src/app
```

## Development

### Install dev dependencies
```bash
pip install -e ".[dev]"
```

### Code quality
```bash
# Lint
ruff check src/

# Type check
mypy src/

# Format
ruff format src/
```

## License

MIT
