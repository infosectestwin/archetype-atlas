import os
import vertexai
from vertexai.generative_models import GenerativeModel
from dotenv import load_dotenv

load_dotenv()
project_id = os.getenv("PROJECT_ID") or "archetype-atlas-495220"
location = "us-central1"

models_to_test = [
    "gemini-3.1-flash",
    "gemini-3.1-flash-001",
    "gemini-3.1-flash-preview",
    "gemini-3.0-flash",
    "gemini-3.0-flash-preview",
    "gemini-2.5-flash",
    "gemini-2.0-flash"
]

vertexai.init(project=project_id, location=location)

for model_name in models_to_test:
    print(f"Testing {model_name}...")
    try:
        model = GenerativeModel(model_name)
        response = model.generate_content("Hello")
        print(f"  SUCCESS: {model_name}")
    except Exception as e:
        print(f"  FAILED: {model_name} - {e}")
