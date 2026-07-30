# Model Disclosure

## Primary Model — Gemini 3.6 Flash
| Field | Detail |
|---|---|
| Model Name | Gemini 3.6 Flash |
| LLM or SLM | LLM |
| Use Case | Primary response generation + LLM-as-judge validation |
| Platform Used | Google AI Studio / Gemini API |
| Deployment Type | API |
| Reason for Selection | Native structured JSON mode, strong instruction-following, large context window |
| One Limitation Observed | Free tier capped at 20 requests/day (daily quota, not just per-minute) — caused full pipeline lockout during testing until dual-judge fallback was added |

## Fallback Model — Qwen 3.6 27B (via Groq)
| Field | Detail |
|---|---|
| Model Name | qwen/qwen3.6-27b |
| LLM or SLM | LLM (27B — mid-size) |
| Use Case | Fallback generation + fallback judge when Gemini unavailable |
| Platform Used | Groq |
| Deployment Type | API |
| Reason for Selection | Fast inference; only non-deprecated model available given org-level Groq allow-list restrictions (openai/gpt-oss-120b preferred but not permitted for this account) |
| One Limitation Observed | Required explicit `max_tokens` ceiling increase to avoid truncated JSON on structured output; also observed empty `failed_generation` output under conflicting/adversarial prompt instructions, likely safety-filter related |

## Tertiary Reserve Fallback — Ling 3.0 Flash (via OpenRouter)
| Field | Detail |
|---|---|
| Model Name | inclusionai/ling-3.0-flash:free |
| LLM or SLM | LLM (124B MoE, 5.1B active parameters) |
| Use Case | Reserve fallback generation + reserve judge when BOTH Gemini and Groq are unavailable |
| Platform Used | OpenRouter |
| Deployment Type | API |
| Reason for Selection | Massive 262K context window and highly capable instruction following available in a free tier; acts as the ultimate safety net for catastrophic vendor lockout. |
| One Limitation Observed | Free tier via OpenRouter explicitly expires on August 3, 2026. |
