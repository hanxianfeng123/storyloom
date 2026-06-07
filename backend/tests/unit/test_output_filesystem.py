import pytest
from storyloom.output.filesystem import FilesystemOutput


@pytest.mark.asyncio
async def test_filesystem_publish(tmp_path):
    output = FilesystemOutput(base_path=str(tmp_path))
    result = await output.publish("proj-1", 1, "Chapter content")
    assert result.format == "markdown"
    assert result.size_bytes > 0
    assert result.path.endswith("chapter.md")
    # Verify file was created
    import os
    assert os.path.exists(result.path)
