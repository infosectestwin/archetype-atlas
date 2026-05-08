import os
from google import genai
from dotenv import load_dotenv

load_dotenv()
project_id = os.getenv("PROJECT_ID") or "archetype-atlas-495220"
location = "us-central1"

models_to_test = [
    "gemini-1.5-flash-001",
    "gemini-1.5-flash",
    "gemini-2.0-flash-001",
    "gemini-2.5-flash"
]

client = genai.Client(vertexai=True, project=project_id, location=location)

for model_name in models_to_test:
    print(f"Testing model: {model_name}")
    try:
        response = client.models.generate_content(
            model=model_name,
            contents="Hello"
        )
        print(f" - SUCCESS: {response.text}")
    except Exception as e:
        print(f" - FAILURE: {e}")
