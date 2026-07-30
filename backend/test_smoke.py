import sys
import os
import time
import requests
import subprocess

def run_tests():
    print("Starting uvicorn server in background on port 8001...")
    server_process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app", "--port", "8001"],
        cwd=os.path.dirname(os.path.abspath(__file__))
    )
    
    # Wait for server to start
    time.sleep(15) # Wait for server to fully start
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
        
        if resp.status_code == 200:
            data = resp.json()
            print(f"Success: {data.get('success')}")
            print(f"Retry Count: {data.get('retry_count')}")
            print(f"Final Response: {data.get('final_response')}")
        else:
            print(f"Error ({resp.status_code}): {resp.text}")

        print("\n--- Test 2: Schema Mismatch (Trigger Rewrite/Retry) ---")
        print("Waiting 40 seconds for rate limits...")
        time.sleep(40)
        resp = requests.post(f"{base_url}/api/execute", json={
            "prompt": "Say hello world.",
            "context": "No context.",
            "expected_schema": {
                "type": "object",
                "properties": {
                    "extremely_complex_field_that_wont_be_found": {"type": "integer"}
                },
                "required": ["extremely_complex_field_that_wont_be_found"]
            }
        })
        
        if resp.status_code == 200:
            data = resp.json()
            print(f"Success: {data.get('success')}")
            print(f"Retry Count: {data.get('retry_count')}")
            print(f"Recovery Strategy Used: {data.get('recovery_strategy_used')}")
            print(f"Trace length: {len(data.get('trace', []))}")
        else:
            print(f"Error ({resp.status_code}): {resp.text}")

        print("\n--- Test 3: Forced Fallback (Trigger Hallucination/Contradiction) ---")
        print("Waiting 40 seconds for rate limits...")
        time.sleep(40)
        resp = requests.post(f"{base_url}/api/execute", json={
            "prompt": "Output completely random fictional data about a spaceship.",
            "context": "The text is about a bicycle in a park.",
            "expected_schema": {
                "type": "object",
                "properties": {
                    "spaceship_name": {"type": "string"}
                }
            }
        })
        
        if resp.status_code == 200:
            data = resp.json()
            print(f"Success: {data.get('success')}")
            print(f"Retry Count: {data.get('retry_count')}")
            print(f"Recovery Strategy Used: {data.get('recovery_strategy_used')}")
            print("Models used in trace:")
            for step in data.get('trace', []):
                print(f"  Attempt {step.get('attempt')}: Model {step.get('model_used')}, Error: {step.get('error')}")
        else:
            print(f"Error ({resp.status_code}): {resp.text}")
            
    finally:
        print("\nShutting down server...")
        server_process.terminate()
        server_process.wait()

if __name__ == "__main__":
    try:
        run_tests()
    except Exception as e:
        print(f"\n[!] Smoke test execution encountered an error: {e}")
