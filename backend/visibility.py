from difflib import SequenceMatcher
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed

from backend.llm import ask_openai, ask_gemini

SIMILARITY_THRESHOLD = 0.85

VISIBILITY_SYSTEM_PROMPT = """
You are a neutral market analyst.

Your task is to answer user queries by listing
well-known brands, companies, or tools relevant to the query.

Rules:
- Respond ONLY with a simple list of names
- One brand per line
- Do NOT include descriptions
"""


def similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def is_brand_visible(brand: str, brands: list[str]) -> bool:
    return any(similarity(brand, b) >= SIMILARITY_THRESHOLD for b in brands)


def process_prompt(prompt: str, brand: str):
    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = {
            executor.submit(ask_openai, prompt, VISIBILITY_SYSTEM_PROMPT): "openai",
            executor.submit(ask_gemini, prompt, VISIBILITY_SYSTEM_PROMPT): "gemini",
        }

        openai_brands = []
        gemini_brands = []

        for future in as_completed(futures):
            source = futures[future]
            try:
                result = future.result()
                if source == "openai":
                    openai_brands = result
                else:
                    gemini_brands = result
            except Exception as e:
                print(f"⚠️ {source.upper()} failed:", e)

    found_openai = is_brand_visible(brand, openai_brands)
    found_gemini = is_brand_visible(brand, gemini_brands)

    combined = list(set(openai_brands + gemini_brands))
    top_3 = [b for b, _ in Counter(combined).most_common(3)]

    return {
        "prompt": prompt,
        "brand_found": found_openai or found_gemini,
        "found_in_openai": found_openai,
        "found_in_gemini": found_gemini,
        "top_3_brands": top_3,
        "openai_brands": openai_brands,
        "gemini_brands": gemini_brands
    }


def check_visibility(prompts: list[str], brand: str):
    results = []
    appeared = 0

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [
            executor.submit(process_prompt, p, brand)
            for p in prompts
        ]

        for future in as_completed(futures):
            r = future.result()
            results.append(r)
            if r["brand_found"]:
                appeared += 1

    total = len(results)

    return {
        "total_prompts": total,
        "appeared": appeared,
        "visibility_percentage": round((appeared / total) * 100, 2) if total else 0,
        "details": results
    }
