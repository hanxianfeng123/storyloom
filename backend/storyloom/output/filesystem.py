from pathlib import Path
import aiofiles
from storyloom.output.base import OutputAdapter, PublishResult


class FilesystemOutput(OutputAdapter):
    def __init__(self, base_path: str = "./works"):
        self.base_path = Path(base_path)

    async def publish(self, project_id: str, chapter_number: int, content: str) -> PublishResult:
        output_dir = self.base_path / project_id / "chapters" / f"ch-{chapter_number:03d}"
        output_dir.mkdir(parents=True, exist_ok=True)
        filepath = output_dir / "chapter.md"
        async with aiofiles.open(filepath, "w", encoding="utf-8") as f:
            await f.write(content)
        return PublishResult(
            path=str(filepath),
            format="markdown",
            size_bytes=len(content.encode("utf-8")),
        )
