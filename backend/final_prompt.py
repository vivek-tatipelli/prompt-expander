from backend.llm import ask_openai

FINAL_PROMPT_SYSTEM = """
You are a senior Marketing Strategist specializing in AI discovery.

Your task is to generate ONE high-quality, verbose discovery query
used to evaluate AI brand visibility.

STRICT RULES:
- Output ONLY the final prompt text
- Do NOT use first-person language (no "I", "we", "my")
- Do NOT include greetings, filler, or conversational phrases
- Do NOT include explanations or context
- Do NOT mention any brand names
- The prompt must read like an expert-level search or AI query
- Focus on discovery, comparison, and recommendation intent
- The result must be ONE clear, well-structured sentence
"""

def generate_final_verbose_prompt(
    seed_keyword: str,
    semantic_keywords: list[str],
    market: str
) -> str:
    prompt = f"""
Service domain: "{seed_keyword}"
Related service terms: {", ".join(semantic_keywords)}
Target market: {market}

Generate ONE authoritative discovery-style query that could be
used to evaluate which brands or solutions are most visible
in AI-generated answers for this service domain.
"""

    response = ask_openai(prompt, system=FINAL_PROMPT_SYSTEM)

    return response[0] if response else ""
