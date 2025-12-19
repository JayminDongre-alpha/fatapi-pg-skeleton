"""Database CLI commands."""

import asyncio
import subprocess
import sys

import typer
from rich.console import Console

app = typer.Typer()
console = Console()


@app.command()
def migrate(
    message: str = typer.Option(None, "--message", "-m", help="Migration message"),
) -> None:
    """Run database migrations using Alembic."""
    if message:
        # Generate new migration
        console.print(f"[yellow]Generating migration: {message}[/yellow]")
        subprocess.run(["alembic", "revision", "--autogenerate", "-m", message], check=False)
    else:
        # Apply migrations
        console.print("[yellow]Applying migrations...[/yellow]")
        subprocess.run(["alembic", "upgrade", "head"], check=False)
        console.print("[green]Migrations applied successfully![/green]")


@app.command()
def rollback(
    steps: int = typer.Option(1, "--steps", "-s", help="Number of migrations to rollback"),
) -> None:
    """Rollback database migrations."""
    console.print(f"[yellow]Rolling back {steps} migration(s)...[/yellow]")
    subprocess.run(["alembic", "downgrade", f"-{steps}"], check=False)
    console.print("[green]Rollback complete![/green]")


@app.command()
def seed() -> None:
    """Seed the database with initial data."""

    async def run_seed() -> None:
        sys.path.insert(0, "src")
        from app.core.config import get_settings
        from app.models.postgres.database import DatabaseSessionManager
        from app.models.postgres.user import User

        settings = get_settings()
        db_manager = DatabaseSessionManager()
        await db_manager.init(settings.database_url)

        async with db_manager.session() as session:
            # Check if admin user already exists
            from sqlalchemy import select

            query = select(User).where(User.email == "admin@example.com")
            result = await session.execute(query)
            if result.scalar_one_or_none():
                console.print("[yellow]Admin user already exists, skipping seed.[/yellow]")
                return

            # Add seed data
            admin_user = User(
                email="admin@example.com",
                hashed_password="hashed_password_here",  # TODO: Hash in production
                full_name="Admin User",
                is_active=True,
                is_superuser=True,
            )
            session.add(admin_user)

        await db_manager.close()
        console.print("[green]Database seeded successfully![/green]")

    asyncio.run(run_seed())


@app.command()
def reset(
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation"),
) -> None:
    """Reset the database (drop all tables and recreate)."""
    if not force:
        confirm = typer.confirm("This will delete all data. Are you sure?")
        if not confirm:
            raise typer.Abort()

    console.print("[red]Resetting database...[/red]")
    subprocess.run(["alembic", "downgrade", "base"], check=False)
    subprocess.run(["alembic", "upgrade", "head"], check=False)
    console.print("[green]Database reset complete![/green]")


@app.command()
def stamp(
    revision: str = typer.Argument(default="head", help="Revision to stamp (default: head)"),
) -> None:
    """Stamp database with revision without running migrations.

    Use this to sync Alembic's version tracking with your database state.
    Common use cases:
    - Fresh database: stamp head before generating first migration
    - Fix 'Target database is not up to date' errors
    """
    console.print(f"[yellow]Stamping database with revision: {revision}[/yellow]")
    subprocess.run(["alembic", "stamp", revision], check=False)
    console.print("[green]Database stamped successfully![/green]")


@app.command()
def current() -> None:
    """Show current database migration revision."""
    subprocess.run(["alembic", "current"], check=False)


@app.command()
def history() -> None:
    """Show database migration history."""
    subprocess.run(["alembic", "history", "--verbose"], check=False)
