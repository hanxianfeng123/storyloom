

class LLMError(Exception):
    def __init__(self, message: str, model: str = ""):
        self.model = model
        super().__init__(message)


class ProviderError(LLMError):
    def __init__(self, message: str, provider: str = "", status_code: int = 0, model: str = ""):
        self.provider = provider
        self.status_code = status_code
        super().__init__(message, model)


class StageError(Exception):
    def __init__(self, message: str, stage: str = ""):
        self.stage = stage
        super().__init__(message)


class PipelineError(Exception):
    def __init__(self, message: str, pipeline_id: str = ""):
        self.pipeline_id = pipeline_id
        super().__init__(message)


class MemoryError(Exception):
    pass


retry_config = {
    "max_retries": 3,
    "backoff_exponential_base": 2,
    "initial_delay_sec": 1,
    "retryable_errors": ["RateLimitError", "TimeoutError", "ServiceUnavailableError"],
}
