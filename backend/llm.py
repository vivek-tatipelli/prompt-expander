from openai import OpenAI
from google import genai
from backend.config import OPENAI_API_KEY, MODEL, GEMINI_API_KEY, GEMINI_MODEL
from google.genai.errors import ClientError, ServerError
import time
import threading

# -----------------------------
# GLOBAL SAFETY CONTROLS
# -----------------------------

OPENAI_SEMAPHORE = threading.Semaphore(10)   # max 10 concurrent OpenAI calls
GEMINI_SEMAPHORE = threading.Semaphore(3)    # max 3 concurrent Gemini calls

GEMINI_LOCK = threading.Lock()
LAST_CALL = 0
MIN_INTERVAL = 1.5  # seconds (free tier safety)

# -----------------------------
# CLIENTS
# -----------------------------

openai_client = OpenAI(api_key=OPENAI_API_KEY)
client = genai.Client(api_key=GEMINI_API_KEY)

# -----------------------------
# OPENAI
# -----------------------------

def ask_openai(prompt: str, system: str) -> list[str]:
    try:
        with OPENAI_SEMAPHORE:
            response = openai_client.responses.create(
                model=MODEL,
                input=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": prompt}
                ]
            )

        text = response.output_text or ""
        return [
            line.strip().lower()
            for line in text.split("\n")
            if line.strip()
        ]

    except Exception as e:
        print("⚠️ OpenAI failure:", e)
        return []

# -----------------------------
# GEMINI
# -----------------------------

def ask_gemini(prompt: str, system: str) -> list[str]:
    global LAST_CALL

    try:
        with GEMINI_SEMAPHORE:
            # ---- soft rate limiting ----
            with GEMINI_LOCK:
                now = time.time()
                if now - LAST_CALL < MIN_INTERVAL:
                    time.sleep(MIN_INTERVAL - (now - LAST_CALL))
                LAST_CALL = time.time()

            response = client.models.generate_content(
                model=GEMINI_MODEL,
                contents=f"{system}\n\n{prompt}"
            )

        text = response.text or ""
        return [
            line.strip().lower()
            for line in text.split("\n")
            if line.strip()
        ]

    except (ClientError, ServerError) as e:
        print(f"⚠️ Gemini handled error ({type(e).__name__}): {e}")
        return []

    except Exception as e:
        print("⚠️ Unexpected Gemini failure:", e)
        return []
