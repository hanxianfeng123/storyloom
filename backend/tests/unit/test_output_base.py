import pytest
from storyloom.output.base import OutputAdapter, PublishResult


def test_publish_result_creation():
    result = PublishResult(path="/tmp/test.md", format="markdown", size_bytes=100)
    assert result.path == "/tmp/test.md"
    assert result.format == "markdown"


def test_output_adapter_is_abstract():
    with pytest.raises(TypeError):
        OutputAdapter()
