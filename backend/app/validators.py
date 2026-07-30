import json
from .llm_clients import call_gemini, call_groq, call_openrouter
from .models import ValidationResult
from .json_guard import safe_json_parse

EVALUATOR_PROMPT_TEMPLATE = """
You are an expert AI evaluator. Evaluate a generated response against the original prompt and context.

Evaluate on 4 criteria (0.0-1.0, where 1.0 is best for Grounding/Completeness, WORST for Contradiction/Hallucination):

IMPORTANT SCORING RULES:
- If a required field is null, empty, or a placeholder because the requested information is genuinely absent from the context, do NOT automatically score Completeness as 1.0. Score Completeness based on whether the response correctly and explicitly signals "not found" rather than silently returning null — a bare null with no explanation should score Completeness around 0.3-0.5, not 1.0.
- Grounding should reflect whether every non-null claim in the response is directly traceable to the context. A response with zero populated fields cannot score above 0.5 Grounding, since there is nothing to verify as grounded.
- If the prompt asks for information that does not exist in the context at all, flag this in "issues" as an extraction-impossible case, and recommend the caller reconsider the prompt/schema — don't reward null output as if it were a successful extraction.

Original Prompt:
{prompt}

Context:
{context}

Generated Response:
{response}

Output ONLY a JSON object with the following structure:
{{
    "grounding_score": 0.0,
    "completeness_score": 0.0,
    "contradiction_score": 0.0,
    "hallucination_score": 0.0,
    "issues": ["list", "of", "issues", "if", "any"],
    "recommended_action": "short actionable suggestion, or null if fully valid"
}}
"""

async def evaluate_response(prompt: str, context: str, response: str) -> ValidationResult:
    """Evaluates response using Gemini as judge."""
    eval_prompt = EVALUATOR_PROMPT_TEMPLATE.format(
        prompt=prompt, 
        context=context or "No context provided.", 
        response=response
    )
    
    try:
        try:
            raw_eval = await call_gemini(eval_prompt, json_mode=True)
            judge_model = "gemini"
        except Exception as gemini_err:
            try:
                raw_eval = await call_groq(eval_prompt, json_mode=True, max_tokens=4096)
                judge_model = "groq"
            except Exception as groq_err:
                try:
                    raw_eval = await call_openrouter(eval_prompt, json_mode=True, max_tokens=4096)
                    judge_model = "openrouter"
                except Exception as openrouter_err:
                    return ValidationResult(is_valid=False, issues=[f"All judges unavailable: {gemini_err} | {groq_err} | {openrouter_err}"])
            
        ok, eval_dict, err = safe_json_parse(raw_eval)
        if not ok:
            return ValidationResult(is_valid=False, issues=[f"Judge output unparseable ({judge_model}): {err}"])
            
        grounding = float(eval_dict.get("grounding_score", 0.0))
        completeness = float(eval_dict.get("completeness_score", 0.0))
        contradiction = float(eval_dict.get("contradiction_score", 0.0))
        hallucination = float(eval_dict.get("hallucination_score", 0.0))
        
        # Heuristic for valid response
        is_valid = (
            hallucination < 0.5 and 
            contradiction < 0.5 and 
            completeness > 0.5 and 
            grounding > 0.5
        )
        quality = ((grounding + completeness + (1.0 - contradiction) + (1.0 - hallucination)) / 4.0)
        
        return ValidationResult(
            is_valid=is_valid,
            quality_score=round(quality, 2),
            grounding_score=grounding,
            completeness_score=completeness,
            contradiction_score=contradiction,
            hallucination_score=hallucination,
            issues=eval_dict.get("issues", []),
            recommended_action=eval_dict.get("recommended_action")
        )
    except Exception as e:
        return ValidationResult(is_valid=False, issues=[f"Evaluation failed: {str(e)}"])

def validate_schema(parsed_response: dict, expected_schema: dict) -> list:
    """Basic structural validation against JSON Schema"""
    issues = []
    required_fields = expected_schema.get("required", [])
    for field in required_fields:
        if field not in parsed_response:
            issues.append(f"Missing required field: {field}")
        elif parsed_response[field] is None:
            issues.append(f"Required field present but null: {field}")
            
    return issues
