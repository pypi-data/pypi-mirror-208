class AsyncIterator:
    items = []
    def __init__(self, items=None):
        if items:
            self.items = items

    def add_item(self, item):
        self.items.append(item)

    async def __aiter__(self):
        for item in self.items:
            yield item