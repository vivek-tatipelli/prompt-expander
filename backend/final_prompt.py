from backend.llm import ask_openai

EXPAND_PROMPT_SYSTEM = """
You are a senior Marketing Strategist specializing in AI discovery behavior.

Your task is to convert a short discovery-style search query
into ONE high-quality, natural user query.

CRITICAL RULES:
- Output MUST be written as a natural search or AI query
- Do NOT write instructions or requests (no "please", "can you", "provide")
- Do NOT use first-person language ("I", "we", "my")
- Do NOT mention brands
- Do NOT add greetings or filler
- The result should sound like something a real user would type
- Keep it concise but detailed (1–2 sentences max)
"""

def expand_existing_prompt(
    short_prompt: str,
    market: str
) -> str:
    prompt = f"""
Base query: "{short_prompt}"
Target market: {market}

Rewrite this as ONE natural, high-intent discovery query
focused on comparison and evaluation.
"""

    response = ask_openai(prompt, system=EXPAND_PROMPT_SYSTEM)

    return " ".join(response)
