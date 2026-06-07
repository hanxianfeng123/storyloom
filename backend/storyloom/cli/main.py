"""Storyloom CLI entry point."""
import typer

app = typer.Typer(name="storyloom")


@app.command()
def init(project_name: str):
    """Initialize a new novel project."""
    typer.echo(f"Initializing project: {project_name}")


@app.command()
def serve(host: str = "127.0.0.1", port: int = 8000):
    """Start the Storyloom web server."""
    typer.echo(f"Starting server on {host}:{port}")


@app.command()
def run(chapter: str):
    """Run the pipeline headless for one or more chapters."""
    typer.echo(f"Running pipeline for chapter(s): {chapter}")


if __name__ == "__main__":
    app()
