# safety.py
import google.generativeai as genai
import os

# Load Gemini API key
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Initialize model
_model = genai.GenerativeModel("models/gemini-2.0-flash")


def is_safe_input(prompt: str) -> bool:
    """
    Classify user input as safe or unsafe.
    Returns True if safe, False if unsafe.
    """
    instruction = """
You are a safety classifier. 
Respond ONLY with one word: SAFE or UNSAFE.
Unsafe includes: violence, hacking, self-harm, scams, illegal activity, malware, etc.
    """

    resp = _model.generate_content(
        f"{instruction}\n\nUser Input:\n{prompt}",
        generation_config={"temperature": 0.0, "max_output_tokens": 10}
    )

    text = getattr(resp, "text", "").strip().upper()

    if "UNSAFE" in text:
        return False
    if "SAFE" in text:
        return True

    # fallback if model gives weird output
    return False  # safer default


def sanitize_output(response_text: str) -> str:
    """
    Post-process LLM output to remove harmful or unsafe content.
    """
    instruction = """
You are a safety filter.
If the text contains unsafe, harmful, violent, hacking-related,
or illegal instructions, return exactly: [REDACTED]
Otherwise, return the text unchanged.
    """

    resp = _model.generate_content(
        f"{instruction}\n\nText:\n{response_text}",
        generation_config={"temperature": 0.0, "max_output_tokens": 1024}
    )

    return getattr(resp, "text", "").strip()
