from backend.llm import ask_openai

SEMANTIC_SYSTEM_PROMPT = """
You are an expert in user search behavior and intent analysis.

Your task is to expand a seed keyword into semantically related
keywords that users might naturally search for.

Rules:
- Return only keyword phrases
- One keyword per line
- Do NOT include explanations
- Do NOT include numbering or bullets
"""


def expand_semantic_keywords(seed: str) -> list:
    prompt = f"""
    You are a Marketing Strategist.

    Expand the seed keyword "{seed}" into exactly 2 keyword phrases
    that represent the same or closely related service intent.

    IMPORTANT RULES:
    - The FIRST keyword MUST be the seed keyword itself: "{seed}"
    - The remaining keywords should be semantically related services
      or alternative ways users search for the same solution
    - One keyword per line
    - Do NOT include explanations, numbering, or bullets
    """

    response = ask_openai(prompt, system=SEMANTIC_SYSTEM_PROMPT)

    return [line.strip() for line in response if line.strip()]

