import os
import random
import time

from dotenv import load_dotenv
from google import genai
from google.genai import errors

load_dotenv()

# Models are tried in order. If one is busy or unavailable, the next one is used.
MODELS = [
    m.strip()
    for m in os.getenv(
        "GEMINI_MODELS",
        "gemini-3.1-flash-lite,gemini-3.5-flash-lite,gemini-3.8-flash",
    ).split(",")
    if m.strip()
]
if not MODELS:
    raise RuntimeError("GEMINI_MODELS is empty. Set it in your .env file.")

ROUNDS = 3                 # full passes over the model list before giving up
BUSY_CODES = {429, 500, 503}
UNAVAILABLE_CODES = {404}  # model not available to this key: skip straight to the next

_api_key = os.getenv("GEMINI_API_KEY")
if not _api_key:
    raise RuntimeError("GEMINI_API_KEY is not set. Add it to your .env file.")

_client = genai.Client(api_key=_api_key)


def ask_llm(prompt: str) -> str:
    """The single entry point every role uses to call the model.

    Tries each model in MODELS. If all are busy, waits (growing each round, with jitter)
    and tries the whole list again.
    """
    last_error = None
    for round_no in range(1, ROUNDS + 1):
        for model in MODELS:
            try:
                response = _client.models.generate_content(model=model, contents=prompt)
                return response.text
            except errors.APIError as exc:
                last_error = exc
                if exc.code in BUSY_CODES or exc.code in UNAVAILABLE_CODES:
                    print(f"{model} returned {exc.code}. Trying next model...")
                    continue
                raise  # other errors (bad key, bad request) won't fix themselves, so stop

        if round_no < ROUNDS:
            wait = min(30, 5 * 2 ** (round_no - 1)) + random.uniform(0, 2)
            print(f"All models busy. Waiting {wait:.0f}s before round {round_no + 1}...")
            time.sleep(wait)

    raise last_error


def extract_json(text: str) -> dict:
    """Pull the first JSON object out of the model's reply, even if it adds extra text."""
    import json
    import re

    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip())
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end == -1:
        raise ValueError(f"Model did not return JSON:\n{text}")
    return json.loads(text[start : end + 1])


def ask_json(prompt: str, retries: int = 1) -> dict:
    """Ask for JSON. If the reply can't be parsed, ask again up to `retries` times."""
    last_error = None
    for _ in range(retries + 1):
        raw = ask_llm(prompt)
        try:
            return extract_json(raw)
        except ValueError as exc:  # json.JSONDecodeError is a ValueError
            last_error = exc
    raise last_error