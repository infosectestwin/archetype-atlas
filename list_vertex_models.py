import os
from google import genai
from dotenv import load_dotenv

load_dotenv()
project_id = os.getenv("PROJECT_ID") or "archetype-atlas-495220"
location = "us-central1"

print(f"Listing models for Vertex AI (Project: {project_id}, Location: {location}):")
try:
    client = genai.Client(vertexai=True, project=project_id, location=location)
    for m in client.models.list():
        print(f" - {m.name}")
except Exception as e:
    print(f"Error listing Vertex models: {e}")
