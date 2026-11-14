"""Planning consumes similarity results; it does not run scoring algorithms."""
import os
import httpx
from services.shared.contracts import ScoreResponse

class SimilarityClient:
    def __init__(self):self.url=os.getenv('SIMILARITY_URL','http://127.0.0.1:8002')

    async def score(self,request):
        async with httpx.AsyncClient(timeout=60) as client:
            # Sensitivity-only controls do not belong to the scoring contract.
            body=request.model_dump(exclude={'n_samples','seed','alpha'})
            response=await client.post(f'{self.url}/score',json=body)
            response.raise_for_status()
            return ScoreResponse.model_validate(response.json()).model_dump()

    async def health(self):
        async with httpx.AsyncClient(timeout=15) as client:
            response=await client.get(f'{self.url}/health')
            response.raise_for_status()
