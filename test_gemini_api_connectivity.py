import os
from google import genai
from dotenv import load_dotenv

load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

models_to_test = [
    "gemini-2.5-flash",
    "gemini-2.5-pro",
    "gemini-2.0-flash"
]

for model_name in models_to_test:
    print(f"Testing model (Gemini API): {model_name}")
    try:
        response = client.models.generate_content(
            model=model_name,
            contents="Hello"
        )
        print(f" - SUCCESS: {response.text}")
    except Exception as e:
        print(f" - FAILURE: {e}")
