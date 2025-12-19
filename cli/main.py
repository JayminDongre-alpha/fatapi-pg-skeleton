"""Typer CLI entry point."""

import typer
from rich.console import Console

from commands import db, server

# Create main CLI app
app = typer.Typer(
    name="fastapi-skeleton",
    help="CLI for FastAPI Skeleton application",
    add_completion=False,
)

# Register command groups
app.add_typer(db.app, name="db", help="Database management commands")
app.add_typer(server.app, name="server", help="Server management commands")

console = Console()


@app.command()
def version() -> None:
    """Show application version."""
    import sys

    sys.path.insert(0, "src")
    from app.core.config import get_settings

    settings = get_settings()
    console.print(f"[bold]{settings.app_name}[/bold] v{settings.app_version}")


@app.command()
def info() -> None:
    """Show application configuration info."""
    import sys

    sys.path.insert(0, "src")
    from app.core.config import get_settings

    settings = get_settings()
    console.print("[bold]Application Configuration:[/bold]")
    console.print(f"  Name: {settings.app_name}")
    console.print(f"  Version: {settings.app_version}")
    console.print(f"  Environment: {settings.environment}")
    console.print(f"  Debug: {settings.debug}")
    console.print(f"  Host: {settings.host}")
    console.print(f"  Port: {settings.port}")


if __name__ == "__main__":
    app()
