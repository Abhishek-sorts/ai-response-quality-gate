import requests

try:
    res = requests.post('http://127.0.0.1:8000/api/execute', json={
        "prompt": "Say hello",
        "context": "none",
        "expected_schema": {"type": "object", "properties": {"hello": {"type": "string"}}}
    })
    print("Status:", res.status_code)
    print("Response:", res.json())
except Exception as e:
    print("Error:", e)
