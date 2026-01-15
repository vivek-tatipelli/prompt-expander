from openai import OpenAI
from google import genai
from backend.config import OPENAI_API_KEY, MODEL, GEMINI_API_KEY, GEMINI_MODEL

openai_client = OpenAI(api_key=OPENAI_API_KEY)

client = genai.Client(api_key=GEMINI_API_KEY)


def ask_openai(prompt: str, system: str) -> list[str]:
    response = openai_client.responses.create(
        model=MODEL,
        input=[
            {"role": "system", "content": system},
            {"role": "user", "content": prompt}
        ]
    )
    text = response.output_text or ""
    return [l.strip().lower() for l in text.split("\n") if l.strip()]


def ask_gemini(prompt: str, system: str) -> list[str]:
    try:
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=f"{system}\n\n{prompt}"
        )

        text = response.text or ""
        return [l.strip().lower() for l in text.split("\n") if l.strip()]

    except genai.erros.Clienterror as e:
        # Gemini quota exceeded → DO NOT crash backend
        if e.status_code == 429 or "RESOURCE_EXHAUSTED" in str(e):
            print("⚠️ Gemini quota exhausted. Skipping Gemini.")
            return []   # critical: safe fallback

        raise e
