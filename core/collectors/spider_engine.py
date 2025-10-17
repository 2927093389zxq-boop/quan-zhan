import asyncio, aiohttp

class SpiderEngine:
    def __init__(self, concurrency=4):
        self.semaphore = asyncio.Semaphore(concurrency)

    async def fetch_one(self, session, url):
        async with self.semaphore:
            async with session.get(url, timeout=15) as r:
                return await r.text()

    async def run(self, urls):
        async with aiohttp.ClientSession() as s:
            tasks = [self.fetch_one(s,u) for u in urls]
            return await asyncio.gather(*tasks, return_exceptions=True)

    def collect(self, urls):
        return asyncio.run(self.run(urls))
