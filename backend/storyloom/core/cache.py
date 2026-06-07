import hashlib
import json
from collections import OrderedDict

from storyloom.providers.base import LLMResponse


class LLMCache:
    """Simple LRU cache for LLM responses. Keyed by model + message hash."""

    def __init__(self, max_size: int = 100):
        self._cache: OrderedDict[str, LLMResponse] = OrderedDict()
        self.max_size = max_size

    def make_key(self, model: str, messages: list) -> str:
        items = []
        for m in messages:
            if isinstance(m, dict):
                items.append({"role": m["role"], "content": m["content"]})
            else:
                items.append({"role": m.role, "content": m.content})
        raw = model + json.dumps(items, sort_keys=True)
        return hashlib.sha256(raw.encode()).hexdigest()[:16]

    def get(self, key: str) -> LLMResponse | None:
        if key in self._cache:
            self._cache.move_to_end(key)
            return self._cache[key]
        return None

    def put(self, key: str, response: LLMResponse) -> None:
        self._cache[key] = response
        self._cache.move_to_end(key)
        while len(self._cache) > self.max_size:
            self._cache.popitem(last=False)

    def clear(self) -> None:
        self._cache.clear()
