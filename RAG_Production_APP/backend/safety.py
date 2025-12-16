# safety.py
import os
import asyncio
from google import genai
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
MODEL_NAME = "gemini-2.5-flash"

async def is_safe_input(prompt: str) -> bool:
    """
    Async safety check for user input.
    Returns True if safe, False if unsafe.
    """
    instruction = (
        "You are a safety classifier. "
        "Respond ONLY with one word: SAFE or UNSAFE. "
        "Unsafe includes: violence, hacking, self-harm, scams, illegal activity, malware, etc."
    )
    full_prompt = f"{instruction}\n\nUser Input:\n{prompt}"

    try:
        resp = await asyncio.to_thread(
            lambda: client.models.generate_content(
                model=MODEL_NAME,
                contents=full_prompt,
                request={"temperature": 0.0, "max_output_tokens": 10}
            )
        )
        text = getattr(resp, "text", "").strip().upper()
        if "SAFE" in text:
            return True
        if "UNSAFE" in text:
            return False
    except Exception:
        pass

    # fallback: permissive
    return True


async def sanitize_output(response_text: str) -> str:
    """
    Async post-processing of LLM output to remove unsafe content.
    Returns '[REDACTED]' if unsafe content is detected.
    """
    instruction = (
        "You are a safety filter. "
        "If the text contains unsafe, harmful, violent, hacking-related, "
        "or illegal instructions, return exactly: [REDACTED]. "
        "Otherwise, return the text unchanged."
    )
    full_prompt = f"{instruction}\n\nText:\n{response_text}"

    try:
        resp = await asyncio.to_thread(
            lambda: client.models.generate_content(
                model=MODEL_NAME,
                contents=full_prompt,
                request={"temperature": 0.0, "max_output_tokens": 1024}
            )
        )
        return getattr(resp, "text", "").strip()
    except Exception:
        return "[REDACTED]"
