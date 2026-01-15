from fastapi import FastAPI
from collections import Counter

from backend.schemas import AnalysisInput
from backend.semantic import expand_semantic_keywords
from backend.prompts import generate_visibility_prompts
from backend.visibility import check_visibility
from backend.db import save_run

app = FastAPI()


@app.post("/analyze")
def analyze_visibility(data: AnalysisInput):
    print("\n========== NEW ANALYSIS REQUEST ==========")
    print("Email:", data.email)
    print("Seed keyword:", data.seed_keyword)
    print("Brand:", data.brand)
    print("Market:", data.market)

    semantic_keywords = expand_semantic_keywords(data.seed_keyword)
    print("Semantic keywords generated:", semantic_keywords)

    all_results = []
    total_appeared = 0
    total_prompts = 0
    all_top_brands = []

    for sk in semantic_keywords:
        print("\nProcessing semantic keyword:", sk)

        prompts = generate_visibility_prompts(sk, data.market)
        print("Generated prompts:", prompts)

        visibility = check_visibility(prompts, data.brand)

        total_appeared += visibility["appeared"]
        total_prompts += visibility["total_prompts"]

        for item in visibility["details"]:
            item["semantic_keyword"] = sk
            all_results.append(item)
            all_top_brands.extend(item["top_3_brands"])

    final_visibility = round(
        (total_appeared / total_prompts) * 100, 2
    ) if total_prompts else 0


    top_3_overall = [
        brand for brand, _ in Counter(all_top_brands).most_common(3)
    ]

    save_run(
        email=data.email,
        seed_keyword=data.seed_keyword,
        brand=data.brand,
        market=data.market,
        visibility=final_visibility,
        top_3_brands=top_3_overall
    )

    print("\nFINAL VISIBILITY %:", final_visibility)
    print("TOP 3 BRANDS:", top_3_overall)
    print("==========================================\n")

    return {
        "email": data.email,
        "seed_keyword": data.seed_keyword,
        "semantic_keywords": semantic_keywords,
        "brand": data.brand,
        "market": data.market,
        "total_prompts": total_prompts,
        "appeared": total_appeared,
        "visibility_percentage": final_visibility,
        "top_3_brands": top_3_overall,
        "details": all_results
    }
