from storyloom.providers.openai import OpenAIProvider


class OllamaProvider(OpenAIProvider):
    def __init__(self, base_url: str = "http://localhost:11434/v1"):
        super().__init__(api_key="ollama", base_url=base_url)
