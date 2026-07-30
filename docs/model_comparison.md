# Model Comparison

| Dimension | Gemini 3.6 Flash | Qwen 3.6 27B (Groq) | Ling 3.0 Flash (OpenRouter) |
|---|---|---|---|
| Response Quality | Higher — stronger reasoning, better grounding adherence | Good but occasionally requires stricter prompting for equivalent grounding | Highly capable, massive 262K context window |
| Latency | Moderate — standard API latency | Significantly faster — Groq's inference hardware measured ~1.5s vs Gemini's ~8.7s | Slower (~10s) but reliable |
| Structured Output Reliability | High with native JSON mode | Required explicit `max_tokens` tuning + system-prompt injection to reliably close JSON objects | Relies on system-prompt enforcement instead of strict response_format |
| Limitations | Free-tier daily quota (20 req/day) — hard ceiling, not rate-limit-recoverable | Constrained to org-approved model list; can hit safety-filter refusals on adversarial/conflicting prompts | Free tier explicitly expires in Aug 2026 |
| Recommended Use Cases | Primary generation + evaluation judge in low-to-moderate volume production | High-throughput fallback / recovery path where speed matters more than reasoning depth | Reserve fallback for catastrophic vendor lockout |
| Production Recommendation | Use as primary with paid tier to avoid quota lockout | Use as secondary fallback | Use as tertiary reserve |
| Cost vs. Performance | Free tier unusable for production volume; paid tier cost scales with quality gains | Cheaper/faster per call, trade-off is lower structured-output reliability without tuning | Excellent safety net |

*Note: The architecture employs a strict three-tier cascade (Gemini → Groq → OpenRouter). The tertiary OpenRouter tier is purely additive and only engages if both primary and secondary systems encounter catastrophic failure (e.g., quota exhaustion or API downtime).*

## Recovery Strategy Flow
1. **First Failure (Schema Mismatch):** The system uses a **Response Repair** strategy to patch missing JSON fields natively without a costly model regeneration.
2. **Evaluation Failure / Parse Error:** The system issues a **Prompt Rewrite** and retries the same model to fix hallucination or parse issues.
3. **Catastrophic Failure (Quota/Downtime):** The orchestrator instantly pivots through the fallback models (Gemini → Groq → OpenRouter).
4. **Judge Autonomy & Resilience:** The LLM-as-a-judge evaluates responses blindly. Furthermore, a **multi-model judge fallback** ensures evaluation isn't a single point of failure; if the primary judge is unavailable, it cascades down the exact same tiers to complete the evaluation.
