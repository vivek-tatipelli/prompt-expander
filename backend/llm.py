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


def ask_gemini(prompt: str, system_prompt: str = "") -> str:
    """
    Gemini LLM call using new google.genai SDK
    """
    full_prompt = (
        f"{system_prompt}\n\n{prompt}"
        if system_prompt else prompt
    )

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=full_prompt
    )

    text = response.text
    return [l.strip().lower() for l in text.split("\n") if l.strip()]
