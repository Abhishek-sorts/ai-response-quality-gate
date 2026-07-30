import json
import os
import time
import uuid

from .models import ExecuteRequest, ExecuteResponse, TraceStep, ValidationResult
from .llm_clients import call_gemini, call_groq, call_openrouter
from .json_guard import safe_json_parse
from .validators import validate_schema, evaluate_response
from .recovery import classify_failure, select_recovery_strategy, RecoveryStrategy, rewrite_prompt, repair_response
from .trace import TraceTracker
from .db import SessionLocal, ExecutionHistory

MAX_RETRIES = int(os.getenv("MAX_RETRIES", 2))

async def execute_pipeline(request: ExecuteRequest) -> ExecuteResponse:
    execution_id = str(uuid.uuid4())
    tracker = TraceTracker()
    
    current_prompt = request.prompt
    context = request.context
    expected_schema = request.expected_schema
    
    success = False
    final_response = None
    strategy_used = None
    current_model = "gemini"
    repaired_json = None
    
    for attempt in range(1, MAX_RETRIES + 2):
        step_start = time.time()
        model_to_use = current_model
        
        raw_response = ""
        error_msg = ""
        is_valid = False
        parsed_json = {}
        val_result = None
        issues = []
        
        try:
            if repaired_json is not None:
                raw_response = json.dumps(repaired_json)
                repaired_json = None
                is_repair_step = True
            else:
                is_repair_step = False
                # 1. Call Model
                generation_prompt = f"{current_prompt}\n\nContext:\n{context}\n\nExpected JSON Schema:\n{json.dumps(expected_schema, indent=2)}"
                
                if model_to_use == "gemini":
                    raw_response = await call_gemini(generation_prompt, json_mode=True)
                elif model_to_use == "groq":
                    raw_response = await call_groq(generation_prompt, json_mode=True)
                else:
                    raw_response = await call_openrouter(generation_prompt, json_mode=True)
                
            # 2. JSON Guard
            json_success, parsed_json, json_err = safe_json_parse(raw_response)
            
            if not json_success:
                error_msg = json_err
                issues = [json_err]
            else:
                # 3. Schema Validation
                schema_issues = validate_schema(parsed_json, expected_schema)
                if schema_issues:
                    error_msg = "Schema Mismatch"
                    issues = schema_issues
                else:
                    # 4. LLM-as-a-judge Evaluation
                    val_result = await evaluate_response(
                        prompt=current_prompt,
                        context=context,
                        response=json.dumps(parsed_json)
                    )
                    if val_result.is_valid:
                        success = True
                        final_response = parsed_json
                        is_valid = True
                    else:
                        error_msg = "Evaluation Failed"
                        issues = val_result.issues
                        
        except Exception as e:
            error_msg = f"API Error: {repr(e)}"
            issues = [error_msg]

        step_latency = int((time.time() - step_start) * 1000)
        
        step_val = val_result if val_result else ValidationResult(is_valid=False, issues=issues)
        
        failure_type = classify_failure(error_msg, issues) if not success else None
        
        tracker.add_step(TraceStep(
            attempt=attempt,
            model_used=model_to_use,
            latency_ms=step_latency,
            validation_result=step_val,
            raw_response=raw_response,
            error=error_msg if not success else None,
            failure_type=failure_type.value if failure_type else None,
            repair_applied=is_repair_step,
            final_validation=success
        ))
        
        if success:
            break
            
        # 5. Recovery Strategy
        strategy = select_recovery_strategy(attempt, MAX_RETRIES, failure_type)
        strategy_used = strategy.value
        
        if strategy == RecoveryStrategy.ABORT:
            break
        elif strategy == RecoveryStrategy.RESPONSE_REPAIR:
            repaired_json = repair_response(parsed_json, expected_schema)
        elif strategy == RecoveryStrategy.REWRITE_PROMPT:
            current_prompt = rewrite_prompt(current_prompt, error_msg)
        elif strategy == RecoveryStrategy.FALLBACK_MODEL:
            if current_model == "gemini":
                current_model = "groq"
            elif current_model == "groq":
                current_model = "openrouter"
            current_prompt = rewrite_prompt(current_prompt, error_msg)

    total_latency = tracker.get_total_latency()
    
    response = ExecuteResponse(
        execution_id=execution_id,
        final_response=final_response,
        success=success,
        recovery_strategy_used=strategy_used if attempt > 1 else None,
        retry_count=len(tracker.steps) - 1,
        total_latency_ms=total_latency,
        trace=tracker.steps
    )
    
    # Save to DB
    db = SessionLocal()
    try:
        db_record = ExecutionHistory(
            id=execution_id,
            prompt=request.prompt,
            context=request.context,
            expected_schema=json.dumps(request.expected_schema),
            final_response=json.dumps(final_response) if final_response else None,
            success=success,
            recovery_strategy_used=response.recovery_strategy_used,
            total_latency_ms=total_latency,
            trace=json.dumps([s.dict() if hasattr(s, 'dict') else s.model_dump() for s in tracker.steps])
        )
        db.add(db_record)
        db.commit()
    finally:
        db.close()
        
    return response
