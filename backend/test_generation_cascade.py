import asyncio
import json
from app.models import ExecuteRequest
from app.orchestrator import execute_pipeline

from unittest.mock import patch

async def run_test():
    req = ExecuteRequest(
        prompt="Say hello.",
        context="No context",
        expected_schema={"type": "object", "properties": {"hello": {"type": "string"}}}
    )
    
    async def mock_call_gemini(*args, **kwargs):
        raise Exception("API Error: ResourceExhausted('You exceeded your current quota...')")
        
    with patch("app.orchestrator.call_gemini", side_effect=mock_call_gemini):
        resp = await execute_pipeline(req)
        print(json.dumps(resp.model_dump() if hasattr(resp, 'model_dump') else resp.dict(), indent=2))

if __name__ == "__main__":
    asyncio.run(run_test())
