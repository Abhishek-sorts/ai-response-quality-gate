import json
import re
from typing import Any, Dict, Tuple

def safe_json_parse(raw_response: str) -> Tuple[bool, Dict[str, Any], str]:
    """
    Attempts to safely parse JSON from a raw LLM response.
    Returns (success_bool, parsed_dict, error_message).
    """
    if not raw_response:
        return False, {}, "Empty response"
        
    cleaned = raw_response.strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    elif cleaned.startswith("```"):
        cleaned = cleaned[3:]
        
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    cleaned = cleaned.strip()
    
    try:
        parsed = json.loads(cleaned)
        if not isinstance(parsed, dict):
            return False, {}, "Parsed JSON is not an object/dictionary."
        return True, parsed, ""
    except json.JSONDecodeError:
        pass
        
    for pattern in [r"```json\s*(\{.*?\})\s*```", r"(\{.*\})"]:
        m = re.search(pattern, raw_response, re.DOTALL)
        if m:
            try:
                parsed = json.loads(m.group(1))
                if isinstance(parsed, dict):
                    return True, parsed, ""
            except json.JSONDecodeError:
                continue

    return False, {}, "JSON Decode Error: could not extract valid object"
