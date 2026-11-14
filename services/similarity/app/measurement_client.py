"""Fetch validated measurement snapshots via HTTP; never read their files here."""
import asyncio
import os
import time
from types import SimpleNamespace
import httpx
from services.shared.contracts import MeasurementSnapshot

class MeasurementClient:
    def __init__(self):
        self.url=os.getenv('MEASUREMENTS_URL','http://127.0.0.1:8003')
        self.ttl=float(os.getenv('MEASUREMENTS_CACHE_SECONDS','60'))
        self.cache=None
        self.lock=asyncio.Lock()

    async def snapshot(self):
        async with self.lock:
            if self.cache and time.monotonic()-self.cache[0]<self.ttl:return self.cache[1]
            async with httpx.AsyncClient(timeout=15) as client:
                response=await client.get(f'{self.url}/snapshot')
                response.raise_for_status()
                data=MeasurementSnapshot.model_validate(response.json()).model_dump()
            result=SimpleNamespace(**data)
            self.cache=(time.monotonic(),result)
            return result
