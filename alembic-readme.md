# Alembic Database Migrations Guide

A comprehensive guide for managing database migrations with Alembic in this FastAPI project.

## Table of Contents

- [What is Alembic?](#what-is-alembic)
- [Getting Started](#getting-started)
- [Common Commands](#common-commands)
- [Development Workflow](#development-workflow)
- [Production Scenarios](#production-scenarios)
- [Troubleshooting](#troubleshooting)
- [CLI Commands Reference](#cli-commands-reference)

---

## What is Alembic?

Alembic is a database migration tool for SQLAlchemy. It helps you:

- **Track database schema changes** in version control
- **Apply changes incrementally** across environments
- **Rollback changes** when needed
- **Collaborate** with team members on database changes

### Why Use Migrations?

| Without Migrations | With Migrations |
|-------------------|-----------------|
| Manual SQL scripts | Automated, versioned changes |
| "Works on my machine" issues | Consistent across all environments |
| No rollback capability | Easy rollback to any version |
| Hard to track changes | Full history in version control |

---

## Getting Started

### First-Time Setup (Fresh Database)

#### Step 1: Create the Database

```bash
# PostgreSQL
createdb fastapi_skeleton

# Or via psql
psql -U postgres -c "CREATE DATABASE fastapi_skeleton;"
```

#### Step 2: Stamp the Database (Important!)

For a fresh database with no tables, stamp it first to initialize Alembic's tracking:

```bash
python3 cli/main.py db stamp head
```

This creates the `alembic_version` table without running any migrations.

#### Step 3: Generate Initial Migration

```bash
python3 cli/main.py db migrate --message "Initial migration - create users table"
```

This creates a migration file in `alembic/versions/` that contains the SQL to create your tables.

#### Step 4: Apply the Migration

```bash
python3 cli/main.py db migrate
```

This executes the migration and creates the actual tables in your database.

#### Step 5: Verify

```bash
# Check current migration status
python3 cli/main.py db current

# Check migration history
python3 cli/main.py db history
```

### Existing Database Setup

If you're joining a project with an existing database:

```bash
# Pull latest code (includes migration files)
git pull

# Apply any pending migrations
python3 cli/main.py db migrate
```

---

## Common Commands

### Quick Reference

| Command | Description |
|---------|-------------|
| `db migrate` | Apply all pending migrations |
| `db migrate -m "message"` | Generate new migration |
| `db rollback -s 1` | Rollback last migration |
| `db current` | Show current revision |
| `db history` | Show migration history |
| `db stamp head` | Mark database as up-to-date |
| `db reset` | Drop all tables and recreate |

### Generate a New Migration

```bash
# After modifying models, generate migration
python3 cli/main.py db migrate --message "Add email verification fields"
```

**Best practices for migration messages:**
- Use descriptive, action-based messages
- Examples: "Add user roles table", "Add index on email", "Remove deprecated columns"

### Apply Migrations

```bash
# Apply all pending migrations
python3 cli/main.py db migrate
```

### Rollback Migrations

```bash
# Rollback 1 migration
python3 cli/main.py db rollback --steps 1

# Rollback 3 migrations
python3 cli/main.py db rollback --steps 3
```

### Check Status

```bash
# Show current revision
python3 cli/main.py db current

# Show full history
python3 cli/main.py db history
```

### Stamp Database

Use when you need to sync Alembic's tracking without running migrations:

```bash
# Mark as latest version
python3 cli/main.py db stamp head

# Mark as specific revision
python3 cli/main.py db stamp abc123def
```

---

## Development Workflow

### Adding a New Model

1. **Create the model** in `src/app/models/`:

```python
# src/app/models/product.py
from sqlalchemy import String, Integer, Numeric
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base

class Product(Base):
    __tablename__ = "products"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, default=0)
```

2. **Import the model** in `alembic/env.py`:

```python
# Add this import to ensure Alembic detects the model
from app.models.product import Product  # noqa: F401
```

3. **Generate the migration**:

```bash
python3 cli/main.py db migrate --message "Add products table"
```

4. **Review the generated migration** in `alembic/versions/`.

5. **Apply the migration**:

```bash
python3 cli/main.py db migrate
```

### Modifying an Existing Model

1. **Make changes** to your model:

```python
# Add a new field
description: Mapped[str | None] = mapped_column(String(1000), nullable=True)
```

2. **Generate migration**:

```bash
python3 cli/main.py db migrate --message "Add description to products"
```

3. **Review and apply**:

```bash
python3 cli/main.py db migrate
```

### Handling Relationships

When adding foreign keys, ensure the referenced table exists first:

```python
# In your model
from sqlalchemy import ForeignKey

class Order(Base):
    __tablename__ = "orders"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
```

---

## Production Scenarios

### Safe Deployment Workflow

#### Development → Staging → Production

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ Development │ -> │   Staging   │ -> │ Production  │
└─────────────┘    └─────────────┘    └─────────────┘
     │                   │                   │
     │ Generate          │ Test              │ Apply only
     │ migrations        │ migrations        │ tested
     └───────────────────┴───────────────────┘
```

1. **Development**: Generate and test migrations locally
2. **Staging**: Apply migrations, run full test suite
3. **Production**: Apply only after staging verification

#### Pre-Deployment Checklist

```bash
# 1. Check pending migrations
python3 cli/main.py db current
python3 cli/main.py db history

# 2. Backup database (CRITICAL!)
pg_dump -U postgres fastapi_skeleton > backup_$(date +%Y%m%d).sql

# 3. Apply migrations
python3 cli/main.py db migrate

# 4. Verify application works
python3 cli/main.py server run
```

### Rolling Back in Production

**Before rollback:**
1. Assess impact - what data might be lost?
2. Take a fresh backup
3. Notify stakeholders

```bash
# Rollback last migration
python3 cli/main.py db rollback --steps 1

# Verify rollback
python3 cli/main.py db current
```

### Handling Failed Migrations

If a migration fails mid-way:

1. **Check the error** and database state
2. **Fix the migration file** if needed
3. **Rollback** if partially applied:

```bash
python3 cli/main.py db rollback --steps 1
```

4. **Re-apply** after fixing:

```bash
python3 cli/main.py db migrate
```

### Data Migrations vs Schema Migrations

#### Schema Migration (Structure)
Changes table structure - columns, indexes, constraints.

```python
def upgrade():
    op.add_column('users', sa.Column('phone', sa.String(20)))
```

#### Data Migration (Content)
Modifies data within tables.

```python
def upgrade():
    # Add column first
    op.add_column('users', sa.Column('status', sa.String(20)))

    # Then populate with data
    op.execute("UPDATE users SET status = 'active' WHERE is_active = true")
    op.execute("UPDATE users SET status = 'inactive' WHERE is_active = false")
```

**Best Practice**: Keep schema and data migrations separate when possible.

### Multi-Developer Workflow

When multiple developers create migrations:

1. **Pull latest changes** before generating migrations
2. **Check for conflicts** in migration versions
3. **Merge carefully** - migrations should be sequential

```bash
# Before creating new migration
git pull origin main
python3 cli/main.py db migrate  # Apply any new migrations
python3 cli/main.py db migrate --message "Your changes"
```

---

## Troubleshooting

### "Target database is not up to date"

**Cause**: Database version doesn't match expected migration chain.

**Solution**:
```bash
# Option 1: Stamp to current head
python3 cli/main.py db stamp head

# Option 2: Apply pending migrations first
python3 cli/main.py db migrate

# Then retry your command
python3 cli/main.py db migrate --message "Your migration"
```

### "Can't locate revision identified by 'xxx'"

**Cause**: Migration file referenced in database doesn't exist.

**Solution**:
```bash
# Check what revision database thinks it's at
python3 cli/main.py db current

# Stamp to a known good revision or head
python3 cli/main.py db stamp head
```

### Empty Migration Generated

**Cause**: Alembic didn't detect model changes.

**Checklist**:
1. Is the model imported in `alembic/env.py`?
2. Did you save the model file?
3. Is the model using the correct `Base` class?

```python
# alembic/env.py - ensure your model is imported
from app.models.user import User  # noqa: F401
from app.models.product import Product  # noqa: F401  # Add new models here
```

### Migration Conflicts

**Cause**: Two migrations have the same down_revision (branching).

**Solution**:
```bash
# Show branches
alembic branches

# Merge branches
alembic merge -m "merge heads" rev1 rev2
```

### Database Connection Issues

**Error**: `sqlalchemy.exc.OperationalError: could not connect`

**Checklist**:
1. Is PostgreSQL running?
2. Is `DATABASE_URL` correct in `.env`?
3. Does the database exist?

```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Verify connection
psql -U postgres -d fastapi_skeleton -c "SELECT 1;"
```

---

## CLI Commands Reference

| Command | Options | Description |
|---------|---------|-------------|
| `db migrate` | | Apply all pending migrations |
| `db migrate` | `-m, --message TEXT` | Generate new migration with message |
| `db rollback` | `-s, --steps INT` | Rollback N migrations (default: 1) |
| `db current` | | Show current database revision |
| `db history` | | Show all migration history |
| `db stamp` | `REVISION` | Stamp database with revision (default: head) |
| `db seed` | | Seed database with initial data |
| `db reset` | `-f, --force` | Reset database (drop all, recreate) |

### Examples

```bash
# Full workflow example
python3 cli/main.py db stamp head           # Initialize fresh database
python3 cli/main.py db migrate -m "Initial" # Generate first migration
python3 cli/main.py db migrate              # Apply migration
python3 cli/main.py db seed                 # Add seed data
python3 cli/main.py db current              # Verify status
```

---

## File Structure

```
alembic/
├── env.py              # Migration environment config
├── script.py.mako      # Migration template
├── alembic.ini         # Alembic configuration
└── versions/           # Migration files
    ├── 20250115_xxxx_initial.py
    └── 20250116_xxxx_add_products.py
```

## Additional Resources

- [Alembic Official Documentation](https://alembic.sqlalchemy.org/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
