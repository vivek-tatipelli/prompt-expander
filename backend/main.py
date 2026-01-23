from fastapi import FastAPI
from threading import Thread
from collections import Counter
import random

from backend.schemas import AnalysisInput
from backend.semantic import expand_semantic_keywords
from backend.prompts import generate_visibility_prompts
from backend.visibility import check_visibility
from backend.final_prompt import expand_existing_prompt
from backend.db import save_run

from backend.jobs import (
    create_job,
    update_job,
    finish_job,
    fail_job,
    get_job
)

app = FastAPI()


@app.get("/health")
def health():
    return {"status": "ok"}


def run_analysis(job_id: str, data: AnalysisInput):
    try:
        semantic_keywords = expand_semantic_keywords(data.seed_keyword)

        PROMPTS_PER_SEM = 5

        all_results = []
        all_top_brands = []
        total_appeared = 0
        total_prompts = 0

        for sk in semantic_keywords:
            prompts = generate_visibility_prompts(sk, data.market)
            visibility = check_visibility(prompts, data.brand)

            total_appeared += visibility["appeared"]
            total_prompts += visibility["total_prompts"]

            for item in visibility["details"]:
                item["semantic_keyword"] = sk
                all_results.append(item)
                all_top_brands.extend(item["top_3_brands"])

                # ✅ PROMPT-LEVEL PROGRESS
                update_job(job_id, 1)

        final_visibility = round(
            (total_appeared / total_prompts) * 100, 2
        ) if total_prompts else 0

        top_3 = [
            b for b, _ in Counter(all_top_brands).most_common(3)
        ]

        # ---------------------------------
        # PICK REAL PROMPT + EXPAND IT
        # ---------------------------------
        if all_results:
            visible = [r for r in all_results if r["brand_found"]]
            source = random.choice(visible if visible else all_results)

            original_prompt = source["prompt"]
            expanded_prompt = expand_existing_prompt(
                short_prompt=original_prompt,
                market=data.market
            )
        else:
            original_prompt = ""
            expanded_prompt = ""

        save_run(
            email=data.email,
            seed_keyword=data.seed_keyword,
            brand=data.brand,
            market=data.market,
            visibility=final_visibility,
            top_3_brands=top_3
        )

        finish_job(job_id, {
            "email": data.email,
            "seed_keyword": data.seed_keyword,
            "semantic_keywords": semantic_keywords,
            "brand": data.brand,
            "market": data.market,
            "total_prompts": total_prompts,
            "appeared": total_appeared,
            "visibility_percentage": final_visibility,
            "top_3_brands": top_3,
            "best_discovery_prompt": {
                "original": original_prompt,
                "expanded": expanded_prompt
            },
            "details": all_results
        })

    except Exception as e:
        fail_job(job_id, str(e))


@app.post("/analyze/start")
def start_analysis(data: AnalysisInput):
    semantic_keywords = expand_semantic_keywords(data.seed_keyword)
    total_steps = len(semantic_keywords) * 5

    job_id = create_job(total_steps)

    Thread(
        target=run_analysis,
        args=(job_id, data),
        daemon=True
    ).start()

    return {
        "job_id": job_id,
        "total_steps": total_steps
    }


@app.get("/analyze/status/{job_id}")
def analyze_status(job_id: str):
    job = get_job(job_id)
    if not job:
        return {"error": "Job not found"}
    return job
