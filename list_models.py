import os
from google import genai
from dotenv import load_dotenv

load_dotenv()
api_key = os.environ.get("GOOGLE_API_KEY")
client = genai.Client(api_key=api_key)

print("Listing available models:")
try:
    for m in client.models.list():
        # Filtering for models that support content generation using the new SDK attribute
        if m.supported_actions and 'generateContent' in m.supported_actions:
            print(m.name)
except Exception as e:
    print(f"Error listing models: {e}")
