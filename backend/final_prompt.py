from backend.llm import ask_openai

EXPAND_PROMPT_SYSTEM = """
You are a Marketing Strategist specializing in AI search behavior.

Your task is to OUTPUT ONLY ONE expanded discovery-style query.

ABSOLUTE RULES:
- Output must be a SINGLE natural search / AI query
- Do NOT write instructions, requests, or commands
- Do NOT use "please", "can you", "help", "provide", "explain"
- Do NOT use first-person language ("I", "we", "my")
- Do NOT mention brands
- Do NOT add introductions or conclusions
- The output must start directly as a query, not a sentence to someone
- The output must be suitable for copy-paste into an AI search box

If the output sounds instructional, it is WRONG.
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
