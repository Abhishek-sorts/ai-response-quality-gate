import asyncio
import json
from unittest.mock import patch
from app.models import ExecuteRequest
from app.orchestrator import execute_pipeline
from app.validators import ValidationResult

async def run_test():
    req = ExecuteRequest(
        prompt="Respond with a JSON object containing the word 'bananas' regardless of context.",
        context="The topic is strictly about apples.",
        expected_schema={"type": "object", "properties": {"hello": {"type": "string"}}}
    )
    
    # We want to mock the evaluator calls to gemini and groq to fail.
    # We will patch them inside validators.py
    
    async def mock_call_gemini_judge(*args, **kwargs):
        raise Exception("Judge Error: Gemini is down")
        
    async def mock_call_groq_judge(*args, **kwargs):
        raise Exception("Judge Error: Groq is down")

    with patch("app.validators.call_gemini", side_effect=mock_call_gemini_judge), \
         patch("app.validators.call_groq", side_effect=mock_call_groq_judge):
        
        resp = await execute_pipeline(req)
        print(json.dumps(resp.model_dump() if hasattr(resp, 'model_dump') else resp.dict(), indent=2))

if __name__ == "__main__":
    asyncio.run(run_test())
