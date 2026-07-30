import os
import asyncio
import google.generativeai as genai
from groq import AsyncGroq
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
gemini_model_name = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")
gemini_model = genai.GenerativeModel(gemini_model_name)

groq_client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))
groq_model_name = os.getenv("GROQ_FALLBACK_MODEL", "qwen/qwen3.6-27b")

openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
openrouter_client = AsyncOpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=openrouter_api_key
) if openrouter_api_key else None
openrouter_model_name = "inclusionai/ling-3.0-flash:free"

async def call_gemini(prompt: str, json_mode: bool = True, retries: int = 1) -> str:
    """Calls Gemini model with retry backoff for rate limits."""
    generation_config = genai.GenerationConfig(
        response_mime_type="application/json" if json_mode else "text/plain"
    )
    try:
        response = gemini_model.generate_content(
            prompt,
            generation_config=generation_config
        )
        return response.text
    except Exception as e:
        if "PerDay" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
            raise  # don't waste time retrying a daily quota — let recovery.py route to fallback immediately
        if "429" in str(e) and retries > 0:
            await asyncio.sleep(20)
            return await call_gemini(prompt, json_mode, retries - 1)
        raise

async def call_groq(prompt: str, json_mode: bool = True, retries: int = 1, max_tokens: int = 2048) -> str:
    """Calls Groq model as fallback."""
    response_format = {"type": "json_object"} if json_mode else {"type": "text"}
    await asyncio.sleep(1.5)  # respect free-tier RPM before every fallback hit
    
    messages = [{"role": "user", "content": prompt}]
    if json_mode:
        messages.insert(0, {"role": "system", "content": "You must respond with valid JSON."})
        
    try:
        chat_completion = await groq_client.chat.completions.create(
            messages=messages,
            model=groq_model_name,
            response_format=response_format,
            max_tokens=max_tokens,
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        if "429" in str(e) and retries > 0:
            await asyncio.sleep(5)
            return await call_groq(prompt, json_mode, retries - 1, max_tokens)
        
        debug_info = f"Groq Error: {repr(e)}"
        if hasattr(e, 'response'):
            debug_info += f" | Response: {getattr(e.response, 'text', '')}"
        elif hasattr(e, 'body'):
            debug_info += f" | Body: {e.body}"
        raise Exception(debug_info) from e

async def call_openrouter(prompt: str, json_mode: bool = True, retries: int = 1, max_tokens: int = 4096) -> str:
    """Calls OpenRouter model as a third-tier reserve fallback."""
    if not openrouter_client:
        raise Exception("OPENROUTER_API_KEY is not set. Cannot invoke third-tier fallback.")
        
    await asyncio.sleep(1.5)
    
    messages = [{"role": "user", "content": prompt}]
    if json_mode:
        messages.insert(0, {"role": "system", "content": "You must respond with valid JSON."})
        
    try:
        chat_completion = await openrouter_client.chat.completions.create(
            messages=messages,
            model=openrouter_model_name,
            max_tokens=max_tokens,
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        if "429" in str(e) and retries > 0:
            await asyncio.sleep(5)
            return await call_openrouter(prompt, json_mode, retries - 1, max_tokens)
            
        debug_info = f"OpenRouter Error: {repr(e)}"
        if hasattr(e, 'response'):
            debug_info += f" | Response: {getattr(e.response, 'text', '')}"
        elif hasattr(e, 'body'):
            debug_info += f" | Body: {e.body}"
        raise Exception(debug_info) from e
