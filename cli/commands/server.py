"""Server CLI commands."""

import code
import sys

import typer
from rich.console import Console

app = typer.Typer()
console = Console()


@app.command()
def run(
    host: str = typer.Option("0.0.0.0", "--host", "-h", help="Host to bind"),
    port: int = typer.Option(8000, "--port", "-p", help="Port to bind"),
    reload: bool = typer.Option(False, "--reload", "-r", help="Enable auto-reload"),
    workers: int = typer.Option(1, "--workers", "-w", help="Number of workers"),
) -> None:
    """Run the FastAPI development server."""
    import uvicorn

    console.print(f"[green]Starting server at http://{host}:{port}[/green]")

    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=reload,
        workers=workers if not reload else 1,
        app_dir="src",
    )


@app.command()
def shell() -> None:
    """Start an interactive Python shell with app context."""
    sys.path.insert(0, "src")

    from app.core.config import get_settings
    from app.models.postgres.database import db_manager
    from app.models.postgres.user import User

    settings = get_settings()

    banner = f"""
FastAPI Skeleton Interactive Shell
==================================
Available objects:
  - settings: Application settings
  - db_manager: Database session manager
  - User: User model

Environment: {settings.environment}
"""

    local_vars = {
        "settings": settings,
        "db_manager": db_manager,
        "User": User,
    }

    code.interact(banner=banner, local=local_vars)


@app.command()
def routes() -> None:
    """List all registered routes."""
    sys.path.insert(0, "src")

    from app.main import app as fastapi_app

    console.print("[bold]Registered Routes:[/bold]\n")

    for route in fastapi_app.routes:
        if hasattr(route, "methods"):
            methods = ", ".join(route.methods)
            console.print(f"  {methods:20} {route.path}")
