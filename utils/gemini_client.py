import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

_client = None


def get_client() -> genai.Client:
    global _client
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY が設定されていません。.env ファイルを確認してください。")
    if _client is None:
        _client = genai.Client(api_key=api_key)
    return _client


MODEL = "gemini-2.5-flash"


def generate(prompt: str, temperature: float = 0.7) -> str:
    client = get_client()
    response = client.models.generate_content(
        model=MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(temperature=temperature),
    )
    return response.text


def stream_generate(prompt: str, temperature: float = 0.7):
    client = get_client()
    for chunk in client.models.generate_content_stream(
        model=MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(temperature=temperature),
    ):
        if chunk.text:
            yield chunk.text
