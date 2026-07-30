# AI Response Quality Gate

A Proof of Concept (POC) that validates AI-generated responses against source content and evaluates quality, reliability, completeness, and accuracy.

## Architecture
- **Backend:** Python / FastAPI
- **Frontend:** React (Vite)
- **Primary Model:** Gemini 3.6 Flash
- **Fallback Model:** Groq (`qwen/qwen3.6-27b`)
- **Tertiary Reserve:** OpenRouter (`inclusionai/ling-3.0-flash:free`)

## Features
- **JSON Guard & Schema Validation** – Ensures structured output adheres to the expected schema
- **LLM-as-a-Judge** – Evaluates Grounding, Completeness, Contradiction, and Hallucination
- **Auto-Healing Orchestrator** – Supports Response Repair, Prompt Rewrite, Retry, and Fallback models
- **AI Execution Debugger** – Shows full execution trace, scores, recovery strategy, latency, and final response

## Setup & Run

### 1. Environment Variables
The `.env` file will be shared separately via email.  
Please place the received `.env` file inside the **project root** folder (`ai-response-quality-gate/`) before running.

(Alternatively you can copy `.env.example` to `.env` and add your own API keys.)

### 2. Backend
```bash
cd backend
python -m venv venv

# Windows
.\venv\Scripts\activate

# Mac / Linux
source venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

Then open the URL shown by Vite (usually http://localhost:5173).

Free-tier API quotas (especially Gemini) may cause the primary model to fail on the first attempt. The system automatically falls back to the next available model.
The tertiary model (Ling 3.0 Flash) is a reserve and only used when both primary and secondary models are unavailable.