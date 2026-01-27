import streamlit as st
import requests
from collections import defaultdict
import os
import time

# ---------------------------------
# PAGE CONFIG
# ---------------------------------
st.set_page_config(
    page_title="Brand Visibility Score",
    layout="wide"
)

st.title("🧠 Brand Visibility Score (LLM-Based)")
st.caption(
    "Measures where and how often your brand appears in AI discovery answers"
)

# ---------------------------------
# SIDEBAR INPUTS
# ---------------------------------
with st.sidebar:
    st.subheader("🔧 Analysis Inputs")

    email = st.text_input("Email Address *", placeholder="you@example.com")
    seed = st.text_input("Seed Keyword", "AI chatbot")
    brand = st.text_input("Brand", "example.ai")
    market = st.text_input("Target Market", "India")

    run = st.button("🚀 Run Analysis")

# ---------------------------------
# VALIDATION
# ---------------------------------
if run and not email:
    st.warning("Please enter your email address to continue.")
    st.stop()

# ---------------------------------
# RUN ANALYSIS (JOB-BASED)
# ---------------------------------
if run:
    payload = {
        "email": email,
        "seed_keyword": seed,
        "brand": brand,
        "market": market
    }

    BACKEND_URL = os.getenv("BACKEND_URL")

    if not BACKEND_URL:
        st.error("BACKEND_URL is not configured.")
        st.stop()

    # ---- START JOB ----
    try:
        start_res = requests.post(
            f"{BACKEND_URL}/analyze/start",
            json=payload,
            timeout=30
        )

        if start_res.status_code != 200:
            st.error("Failed to start analysis job.")
            st.stop()

        job_id = start_res.json()["job_id"]

    except Exception as e:
        st.error(f"Failed to start job: {e}")
        st.stop()

    # ---- REAL PROGRESS BAR ----
    st.subheader("⏳ Analysis Progress")

    progress_bar = st.progress(0)
    progress_text = st.empty()

    data = None

    while True:
        try:
            status_res = requests.get(
                f"{BACKEND_URL}/analyze/status/{job_id}",
                timeout=30
            )

            if status_res.status_code != 200:
                st.error("Failed to fetch job status.")
                st.stop()

            status = status_res.json()

        except Exception as e:
            st.error(f"Status polling failed: {e}")
            st.stop()

        if status["status"] == "running":
            progress = int(status.get("progress", 0))
            progress_bar.progress(progress)
            progress_text.text(f"Processing… {progress}% completed")
            time.sleep(1)

        elif status["status"] == "completed":
            progress_bar.progress(100)
            progress_text.text("Analysis complete ✔")
            data = status["result"]
            break

        elif status["status"] == "failed":
            st.error(status.get("error", "Analysis failed"))
            st.stop()

    # ---------------------------------
    # OVERALL VISIBILITY
    # ---------------------------------
    st.divider()
    st.subheader("📊 Overall Brand Visibility")

    st.metric(
        label="Visibility %",
        value=f"{data['visibility_percentage']}%",
        delta=f"{data['appeared']} / {data['total_prompts']} prompts"
    )

    # ---------------------------------
    # GROUP BY SEMANTIC KEYWORD
    # ---------------------------------
    st.divider()

    grouped = defaultdict(list)
    for item in data["details"]:
        grouped[item["semantic_keyword"]].append(item)

    st.subheader("🔍 Visibility by Semantic Keyword")

    for semantic, items in grouped.items():
        appeared = sum(1 for i in items if i["brand_found"])
        total = len(items)
        score = round((appeared / total) * 100, 2) if total else 0

        with st.expander(f"🔹 {semantic}", expanded=False):
            st.metric(
                label="Visibility %",
                value=f"{score}%",
                delta=f"{appeared} / {total} prompts"
            )

            st.markdown("**Prompt-level visibility:**")

            for i in items:
                col1, col2, col3, col4 = st.columns([6, 1, 1, 2])

                found_openai = i.get("found_in_openai", False)
                found_gemini = i.get("found_in_gemini", False)

                # ---- Visibility strength logic ----
                if found_openai and found_gemini:
                    strength = "Strong"
                elif found_openai or found_gemini:
                    strength = "Partial"
                else:
                    strength = "Missing"

                with col1:
                    icon = "✅" if i["brand_found"] else "❌"
                    st.markdown(f"{icon} **{i['prompt']}**")

                with col2:
                    st.checkbox(
                        "OpenAI",
                        value=found_openai,
                        disabled=True,
                        key=f"openai_{semantic}_{hash(i['prompt'])}"
                    )

                with col3:
                    st.checkbox(
                        "Gemini",
                        value=found_gemini,
                        disabled=True,
                        key=f"gemini_{semantic}_{hash(i['prompt'])}"
                    )

                with col4:
                    st.markdown(f"**{strength}**")

    # ---------------------------------
    # FINAL TOP 3 BRANDS
    # ---------------------------------
    st.divider()
    st.subheader("🏆 Top 3 Brands Seen Across All LLMs")

    if data.get("top_3_brands"):
        with st.container(border=True):
            for idx, b in enumerate(data["top_3_brands"], start=1):
                st.markdown(f"### {idx}. {b}")
    else:
        st.info("No competing brands detected.")

    # ---------------------------------
    # BEST REAL DISCOVERY PROMPT
    # ---------------------------------
    st.divider()
    st.subheader("🧠 Best Real Discovery Prompt")

    bdp = data.get("best_discovery_prompt")

    if bdp:
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Original user-style prompt**")
            with st.container(border=True):
                st.code(bdp["original"], language="text")

        with col2:
            st.markdown("**Expanded prompt**")

            st.markdown(
                f"""
                <div style="
                    max-height: 260px;
                    overflow-y: auto;
                    padding: 14px;
                    border: 1px solid #e6e6e6;
                    border-radius: 6px;
                    background-color: #0e1117;
                    color: #fafafa;
                    font-family: monospace;
                    white-space: pre-wrap;
                ">
                {bdp["expanded"]}
                </div>
                """,
                unsafe_allow_html=True
            )

    else:
        st.info("No discovery prompt available.")


    # ---------------------------------
    # FINAL INTERPRETATION
    # ---------------------------------
    st.divider()

    if data["visibility_percentage"] < 30:
        st.error("❌ Low AI visibility — brand rarely appears in LLM answers.")
    elif data["visibility_percentage"] < 60:
        st.warning("⚠️ Moderate AI visibility — inconsistent across LLMs.")
    else:
        st.success("✅ Strong AI visibility — brand appears consistently across LLMs.")
