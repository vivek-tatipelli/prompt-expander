import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL = "gpt-4.1-mini"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = "gemini-2.5-flash-lite"
MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB = os.getenv("MONGO_DB","brand_visibility")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION","visibility_runs")
