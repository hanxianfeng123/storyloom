from storyloom.core.logging import get_logger, configure_logging


def test_get_logger_returns_structlog_logger():
    logger = get_logger("test")
    assert hasattr(logger, "info")
    assert hasattr(logger, "error")


def test_configure_logging_sets_level():
    configure_logging("DEBUG")
    logger = get_logger("test_debug")
    # Should not raise
    logger.debug("test message")
