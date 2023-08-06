from typing import Any, Dict, Generator, List, NamedTuple, Optional
import json
import requests

class StreamingGenerations():
    def __init__(self, response):
        self.response = response
        self.items = []

    def _make_response_item(self, line) -> Optional[Any]:
        if line is None:
            return None
        streaming_item = json.loads(line)
        self.items.append(streaming_item)
        return streaming_item

    def __iter__(self) -> Generator[Any, None, None]:
        if not isinstance(self.response, requests.Response):
            raise ValueError("For AsyncClient, use `async for` to iterate through the `StreamingGenerations`")

        for line in self.response.iter_lines():
            item = self._make_response_item(line)
            if item is not None:
                yield item

    async def __aiter__(self) -> Generator[Any, None, None]:
        async for line in self.response:
            item = self._make_response_item(line)
            if item is not None:
                yield item