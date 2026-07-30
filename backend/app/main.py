from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import json

from .models import ExecuteRequest, ExecuteResponse
from .orchestrator import execute_pipeline
from .db import init_db, SessionLocal, ExecutionHistory

load_dotenv()

init_db()

app = FastAPI(title="AI Response Quality Gate")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/api/execute", response_model=ExecuteResponse)
async def execute(request: ExecuteRequest):
    response = await execute_pipeline(request)
    return response

@app.get("/api/execution/{id}")
def get_execution(id: str):
    db = SessionLocal()
    try:
        record = db.query(ExecutionHistory).filter(ExecutionHistory.id == id).first()
        if not record:
            raise HTTPException(status_code=404, detail="Execution not found")
        return {
            "execution_id": record.id,
            "prompt": record.prompt,
            "context": record.context,
            "expected_schema": json.loads(record.expected_schema),
            "final_response": json.loads(record.final_response) if record.final_response else None,
            "success": record.success,
            "recovery_strategy_used": record.recovery_strategy_used,
            "retry_count": len(json.loads(record.trace)) - 1,
            "total_latency_ms": record.total_latency_ms,
            "trace": json.loads(record.trace)
        }
    finally:
        db.close()

@app.get("/api/failures")
def get_failures():
    db = SessionLocal()
    try:
        records = db.query(ExecutionHistory).filter(ExecutionHistory.success == False).all()
        recovered = db.query(ExecutionHistory).filter(
            ExecutionHistory.success == True,
            ExecutionHistory.recovery_strategy_used != None,
            ExecutionHistory.recovery_strategy_used != "ABORT"
        ).all()
        
        return {
            "total_failures": len(records),
            "total_recovered": len(recovered),
            "failed_executions": [{"id": r.id, "prompt": r.prompt} for r in records],
            "recovered_executions": [{"id": r.id, "recovery_strategy": r.recovery_strategy_used} for r in recovered]
        }
    finally:
        db.close()
