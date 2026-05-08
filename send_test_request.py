import requests
import json

url = "http://localhost:8000/analyze"
payload = {
    "athlete_id": 999,
    "name": "Test Athlete",
    "height_cm": 198.0,
    "weight_kg": 95.0,
    "wingspan_cm": 205.0,
    "sport": "Basketball",
    "year": 2024,
    "is_paralympic": False
}

try:
    print(f"Sending request to {url}...")
    response = requests.post(url, json=payload)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        print("Success!")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"Error: {response.text}")
except Exception as e:
    print(f"Connection failed: {e}")
