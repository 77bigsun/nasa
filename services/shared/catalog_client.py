import asyncio
import os
import time
import httpx
from services.shared.contracts import Bundle

class CatalogClient:
    def __init__(self):
        self.url=os.getenv('CATALOG_URL','http://127.0.0.1:8001')
        self.ttl=float(os.getenv('CATALOG_CACHE_SECONDS','60'))
        self.cache={}
        self.lock=asyncio.Lock()

    async def bundle(self,mission):
        async with self.lock:
            cached=self.cache.get(mission)
            if cached and time.monotonic()-cached[0]<self.ttl:return cached[1]
            async with httpx.AsyncClient(timeout=15) as client:
                response=await client.get(f'{self.url}/missions/{mission}/bundle')
                response.raise_for_status()
                data=Bundle.model_validate(response.json()).model_dump()
            self.cache[mission]=(time.monotonic(),data)
            return data

