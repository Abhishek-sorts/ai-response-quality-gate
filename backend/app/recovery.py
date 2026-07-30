from enum import Enum

class FailureType(Enum):
    JSON_PARSE_ERROR = "JSON_PARSE_ERROR"
    SCHEMA_MISMATCH = "SCHEMA_MISMATCH"
    EVALUATION_FAILED = "EVALUATION_FAILED"
    RATE_LIMIT_OR_QUOTA = "RATE_LIMIT_OR_QUOTA"
    API_ERROR = "API_ERROR"

class RecoveryStrategy(Enum):
    RETRY_SAME_MODEL = "RETRY_SAME_MODEL"
    REWRITE_PROMPT = "REWRITE_PROMPT"
    FALLBACK_MODEL = "FALLBACK_MODEL"
    RESPONSE_REPAIR = "RESPONSE_REPAIR"
    ABORT = "ABORT"

def classify_failure(error_message: str, issues: list) -> FailureType:
    if not error_message:
        return FailureType.API_ERROR
    if "429" in error_message or "quota" in error_message.lower() or "RESOURCE_EXHAUSTED" in error_message:
        return FailureType.RATE_LIMIT_OR_QUOTA
    if "JSON Decode Error" in error_message or "not an object" in error_message:
        return FailureType.JSON_PARSE_ERROR
    if any("Missing required field" in i for i in issues):
        return FailureType.SCHEMA_MISMATCH
    if any(k in i.lower() for i in issues for k in ("hallucination", "contradiction", "evaluation failed")):
        return FailureType.EVALUATION_FAILED
    return FailureType.API_ERROR

def select_recovery_strategy(attempt: int, max_retries: int, failure_type: FailureType) -> RecoveryStrategy:
    if failure_type == FailureType.RATE_LIMIT_OR_QUOTA:
        return RecoveryStrategy.FALLBACK_MODEL
    if attempt >= max_retries + 1:
        return RecoveryStrategy.ABORT
        
    if failure_type == FailureType.JSON_PARSE_ERROR:
        return RecoveryStrategy.REWRITE_PROMPT
    elif failure_type == FailureType.SCHEMA_MISMATCH:
        if attempt == 1:
            return RecoveryStrategy.RESPONSE_REPAIR
        return RecoveryStrategy.RETRY_SAME_MODEL if attempt == 2 else RecoveryStrategy.FALLBACK_MODEL
    elif failure_type == FailureType.EVALUATION_FAILED:
        return RecoveryStrategy.REWRITE_PROMPT
    else:
        return RecoveryStrategy.FALLBACK_MODEL

def rewrite_prompt(original_prompt: str, error_message: str) -> str:
    """Modifies the prompt to help the LLM fix the issue."""
    return (
        f"{original_prompt}\n\n"
        f"IMPORTANT: The previous attempt failed validation. "
        f"Ensure the output is grounded strictly in the provided context, contains no fabricated "
        f"or unsupported claims, and is valid JSON matching the requested schema. "
        f"Error details: {error_message}"
    )

def repair_response(parsed_json: dict, expected_schema: dict) -> dict:
    """Attempts to patch a response with missing/malformed fields directly,
    without a full model regeneration."""
    properties = expected_schema.get("properties", {})
    required = expected_schema.get("required", [])
    repaired = dict(parsed_json)
    for field in required:
        if field not in repaired:
            field_type = properties.get(field, {}).get("type", "string")
            repaired[field] = {"string": "", "integer": None, "boolean": None, "array": []}.get(field_type, None)
    return repaired

