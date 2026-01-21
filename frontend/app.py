import streamlit as st
import requests
from collections import defaultdict
import os

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

progress_bar = st.progress(0)
status = st.empty()
# ---------------------------------
# RUN ANALYSIS
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

    try:
        status.text("Running analysis across LLMs...")
        progress_bar.progress(50)

        with st.spinner("Analyzing brand visibility..."):
            res = requests.post(
                f"{BACKEND_URL}/analyze",
                json=payload,
                timeout=600
            )

        if res.status_code != 200:
            st.error("Backend error. Check FastAPI logs.")
            progress_bar.progress(100)
            status.text("Analysis failed")
            st.stop()

        data = res.json()
    
    except Exception as e:
        st.error(f"Request failed: {e}")
        st.stop()

    # ---------------------------------
    # OVERALL VISIBILITY
    # ---------------------------------
    
    st.subheader("📊 Overall Brand Visibility")

    st.metric(
        label="Visibility %",
        value=f"{data['visibility_percentage']}%",
        delta=f"{data['appeared']} / {data['total_prompts']} prompts"
    )

    st.divider()

    # ---------------------------------
    # GROUP BY SEMANTIC KEYWORD
    # ---------------------------------
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
                col1, col2, col3 = st.columns([6, 1, 1])

                with col1:
                    icon = "✅" if i["brand_found"] else "❌"
                    st.markdown(f"{icon} **{i['prompt']}**")

                with col2:
                    st.checkbox(
                        "OpenAI",
                        value=i.get("found_in_openai", False),
                        disabled=True,
                        key=f"openai_{semantic}_{i['prompt']}"
                    )

                with col3:
                    st.checkbox(
                        "Gemini",
                        value=i.get("found_in_gemini", False),
                        disabled=True,
                        key=f"gemini_{semantic}_{i['prompt']}"
                    )

    # ---------------------------------
    # FINAL TOP 3 BRANDS (CARD)
    # ---------------------------------
    st.divider()
    st.subheader("🏆 Top 3 Brands Seen Across All LLMs")

    if data["top_3_brands"]:
        with st.container(border=True):
            for idx, b in enumerate(data["top_3_brands"], start=1):
                st.markdown(f"### {idx}. {b}")
    else:
        st.info("No competing brands detected.")
        
    st.divider()
    st.subheader("🧠 Best Final Discovery Prompt")

    st.markdown(
        "Use this prompt to test or improve your brand’s visibility:"
    )

    with st.container(border=True):
        st.code(data["final_verbose_prompt"], language="text")

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
