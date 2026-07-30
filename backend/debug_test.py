import requests
import json
import time

try:
    base_url = "http://127.0.0.1:8001"
    
    print("\n--- Test 1: Clean Success ---")
    resp = requests.post(f"{base_url}/api/execute", json={
        "prompt": "Extract the user's name and age from the text.",
        "context": "John is 30 years old and lives in New York.",
        "expected_schema": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer"}
            },
            "required": ["name", "age"]
        }
    })
    
    print(json.dumps(resp.json(), indent=2))
except Exception as e:
    print(e)
