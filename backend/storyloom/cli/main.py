"""Storyloom CLI entry point."""
import typer
from storyloom.cli.commands.init import init_project

app = typer.Typer(name="storyloom")


@app.command()
def init(project_name: str):
    """Initialize a new novel project."""
    init_project(project_name)


@app.command()
def serve(host: str = "127.0.0.1", port: int = 8000):
    """Start the Storyloom web server."""
    import uvicorn
    uvicorn.run("storyloom.api.app:app", host=host, port=port, reload=True)


@app.command()
def run(chapter: str, legacy: bool = False):
    """Run the pipeline headless for one or more chapters. Uses LLM-driven supervisor by default."""
    from storyloom.cli.commands.run import run_pipeline
    run_pipeline(chapter, legacy=legacy)


if __name__ == "__main__":
    app()
