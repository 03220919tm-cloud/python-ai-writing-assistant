import os
from google import genai
from google.genai import types
from dotenv import load_dotenv
from utils.api_key import get_api_key

load_dotenv()

_client = None
_client_api_key = None


def get_client() -> genai.Client:
    global _client, _client_api_key
    api_key = get_api_key()
    if not api_key:
        raise ValueError("Gemini API キーが設定されていません。サイドバーに入力するか、.env ファイルを確認してください。")
    if _client is None or _client_api_key != api_key:
        _client = genai.Client(api_key=api_key)
        _client_api_key = api_key
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
