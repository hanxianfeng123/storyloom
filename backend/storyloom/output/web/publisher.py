from pathlib import Path
import markdown
import aiofiles
from storyloom.output.base import OutputAdapter, PublishResult


class WebPublisher(OutputAdapter):
    def __init__(self, output_dir: str = "./works/published/web"):
        self.output_dir = Path(output_dir)

    async def publish(self, project_id: str, chapter_number: int, content: str) -> PublishResult:
        html = markdown.markdown(content, extensions=["extra"])
        chapter_dir = self.output_dir / project_id / f"ch-{chapter_number:03d}"
        chapter_dir.mkdir(parents=True, exist_ok=True)
        filepath = chapter_dir / "index.html"
        async with aiofiles.open(filepath, "w", encoding="utf-8") as f:
            await f.write(f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>{project_id} - Ch {chapter_number}</title>
<style>body {{ max-width: 720px; margin: auto; padding: 2em; line-height: 1.8; }}</style>
</head><body>{html}</body></html>""")
        return PublishResult(path=str(filepath), format="html", size_bytes=len(html.encode("utf-8")))
