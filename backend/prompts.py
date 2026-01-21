from backend.llm import ask_openai


VISIBILITY_PROMPT_SYSTEM = """
You are an expert in user search behavior.

Your task is to generate natural user queries that people ask
when they want to discover top brands, companies, tools,
or platforms for a given service.

Rules:
- Avoid repeating phrasing or sentence structure
- Generate discovery-focused queries
- Each query must be 5–8 words
- Do NOT include brand names
- Do NOT number the list
- Do NOT include explanations
- One query per line
"""

def generate_visibility_prompts(semantic_keyword: str, market: str) -> list:

    prompt = f"""
        You are a Marketing Strategist.

        Your goal is to take a seed keyword and expand it into multiple
        short search prompts that reflect how different types of users
        may discover a brand through AI or search engines.

        Objective:
        - Study the given seed keyword
        - Generate 5 short, natural user search queries
        - Each query should reflect a different discovery intent
        - Queries must sound like real human searches

        Context:
        - Seed keyword / service: "{semantic_keyword}"
        - Target market: "{market}"
    """

    response = ask_openai(prompt, system=VISIBILITY_PROMPT_SYSTEM)

    return [line.strip() for line in response if line.strip()]
