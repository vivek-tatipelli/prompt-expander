from difflib import SequenceMatcher
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed

from backend.llm import ask_openai, ask_gemini

SIMILARITY_THRESHOLD = 0.85

SIMILARITY_THRESHOLD = 0.85

VISIBILITY_SYSTEM_PROMPT = """
You are a neutral market analyst.

Your task is to answer user queries by listing
well-known brands, companies, or tools relevant to the query.

Rules:
- Respond ONLY with a simple list of names
- One brand per line
- Do NOT include descriptions or explanations
- Do NOT include introductory or concluding text
- Do NOT rank unless explicitly asked
- Be factual and neutral
"""

def similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def is_brand_visible(brand: str, brands: list[str]) -> bool:
    for b in brands:
        if similarity(brand, b) >= SIMILARITY_THRESHOLD:
            return True
    return False

def process_prompt(prompt: str, brand: str):
    """
    Process one prompt (OpenAI + Gemini).
    This runs inside a thread.
    """

    openai_brands = ask_openai(prompt, VISIBILITY_SYSTEM_PROMPT)
    found_in_openai = is_brand_visible(brand, openai_brands)

    # Gemini is OPTIONAL (quota safe)
    gemini_brands = ask_gemini(prompt, VISIBILITY_SYSTEM_PROMPT)
    found_in_gemini = bool(gemini_brands) and is_brand_visible(
        brand, gemini_brands
    )

    brand_found = found_in_openai or found_in_gemini

    combined_brands = list(set(openai_brands + gemini_brands))
    top_3_brands = [
        b for b, _ in Counter(combined_brands).most_common(3)
    ]

    return {
        "prompt": prompt,
        "brand_found": brand_found,
        "found_in_openai": found_in_openai,
        "found_in_gemini": found_in_gemini,
        "top_3_brands": top_3_brands,
        "openai_brands": openai_brands,
        "gemini_brands": gemini_brands
    }


def check_visibility(prompts: list[str], brand: str):
    results = []
    appeared = 0

    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [
            executor.submit(process_prompt, prompt, brand)
            for prompt in prompts
        ]

        for future in as_completed(futures):
            result = future.result()
            results.append(result)

            if result["brand_found"]:
                appeared += 1

    total = len(prompts)
    visibility_percentage = round(
        (appeared / total) * 100, 2
    ) if total else 0

    return {
        "total_prompts": total,
        "appeared": appeared,
        "visibility_percentage": visibility_percentage,
        "details": results
    }
