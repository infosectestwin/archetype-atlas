import vertexai
from vertexai.generative_models import GenerativeModel
import os
from dotenv import load_dotenv

load_dotenv()
project_id = os.getenv("PROJECT_ID") or "archetype-atlas-495220"
location = "us-central1"

vertexai.init(project=project_id, location=location)

print(f"Testing Gemini 1.5 Flash with Legacy SDK (Project: {project_id}, Location: {location}):")
try:
    model = GenerativeModel("gemini-1.5-flash-001")
    response = model.generate_content("Hello")
    print(f" - SUCCESS: {response.text}")
except Exception as e:
    print(f" - FAILURE: {e}")
