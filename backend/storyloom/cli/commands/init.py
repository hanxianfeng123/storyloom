from pathlib import Path
import typer


def init_project(project_name: str):
    base = Path.cwd() / project_name
    dirs = ["bible", "chapters", "output"]
    for d in dirs:
        (base / d).mkdir(parents=True, exist_ok=True)
    (base / "bible" / "characters.yaml").write_text("# Characters\n")
    (base / "bible" / "world.yaml").write_text("# World Settings\n")
    (base / "bible" / "plot-threads.yaml").write_text("# Plot Threads\n")
    (base / "outline.yaml").write_text("# Outline\n")
    typer.echo(f"Created project: {project_name}")
