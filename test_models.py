import os

from dotenv import load_dotenv
from google import genai

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

MODELS = [
    "gemini-3.1-flash-lite",
    "gemini-3.5-flash-lite",
    "gemini-3.8-flash",
]

for model in MODELS:
    try:
        reply = client.models.generate_content(model=model, contents="Say hi in three words.")
        print(f"{model}: OK, {reply.text.strip()[:40]}")
    except Exception as exc:
        print(f"{model}: FAILED, {str(exc)[:100]}")