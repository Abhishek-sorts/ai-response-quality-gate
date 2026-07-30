from pydantic import BaseModel
from typing import Any, Dict, Optional, List

class ExecuteRequest(BaseModel):
    prompt: str
    expected_schema: Dict[str, Any]
    context: Optional[str] = None

class ValidationResult(BaseModel):
    is_valid: bool
    quality_score: float = 0.0
    grounding_score: float = 0.0
    completeness_score: float = 0.0
    contradiction_score: float = 0.0
    hallucination_score: float = 0.0
    issues: List[str] = []
    recommended_action: Optional[str] = None

class TraceStep(BaseModel):
    attempt: int
    model_used: str
    latency_ms: int
    validation_result: Optional[ValidationResult] = None
    raw_response: str
    error: Optional[str] = None
    failure_type: Optional[str] = None
    repair_applied: bool = False
    final_validation: bool = False

class ExecuteResponse(BaseModel):
    execution_id: str
    final_response: Optional[Dict[str, Any]] = None
    success: bool
    recovery_strategy_used: Optional[str] = None
    retry_count: int = 0
    total_latency_ms: int
    trace: List[TraceStep]
