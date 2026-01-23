from backend.llm import ask_openai

EXPAND_PROMPT_SYSTEM = """
You are a senior Marketing Strategist.

Your task is to take a SHORT discovery-style search query
and expand it into a single, clear, verbose prompt that
a real user would ask an AI assistant.

Rules:
- Preserve the original intent
- Do NOT add greetings or filler
- Do NOT mention brands
- Make it detailed but natural
"""

def expand_existing_prompt(
    short_prompt: str,
    market: str
) -> str:
    prompt = f"""
Short user query: "{short_prompt}"
Target market: {market}

Expand this into ONE clear, detailed prompt suitable
for testing AI brand visibility.
"""

    response = ask_openai(prompt, system=EXPAND_PROMPT_SYSTEM)

    # ask_openai returns list[str], join safely
    return " ".join(response)
