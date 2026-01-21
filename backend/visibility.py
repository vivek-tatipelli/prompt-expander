import asyncio
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

async def process_prompt(prompt: str, brand: str):
    openai_task = asyncio.to_thread(
        ask_openai, prompt, VISIBILITY_SYSTEM_PROMPT
    )
    gemini_task = asyncio.to_thread(
        ask_gemini, prompt, VISIBILITY_SYSTEM_PROMPT
    )

    openai_result, gemini_result = await asyncio.gather(
        openai_task,
        gemini_task,
        return_exceptions=True
    )

    # Handle OpenAI failure safely
    if isinstance(openai_result, Exception):
        print("⚠️ OpenAI failed:", openai_result)
        openai_brands = []
    else:
        openai_brands = openai_result

    # Handle Gemini failure safely
    if isinstance(gemini_result, Exception):
        print("⚠️ Gemini failed:", gemini_result)
        gemini_brands = []
    else:
        gemini_brands = gemini_result

    found_in_openai = is_brand_visible(brand, openai_brands)
    found_in_gemini = is_brand_visible(brand, gemini_brands)

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

async def check_visibility(prompts: list[str], brand: str):
    tasks = [
        process_prompt(prompt, brand)
        for prompt in prompts
    ]

    results = await asyncio.gather(*tasks)  
    
    valid_results = [
        r for r in results
        if r["openai_brands"] or r["gemini_brands"]
    ]

    appeared = sum(1 for r in valid_results if r["brand_found"])
    total = len(valid_results)

    return {
        "total_prompts": total,
        "appeared": appeared,
        "visibility_percentage": round((appeared / total) * 100, 2) if total else 0,
        "details": results
    }
