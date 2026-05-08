import os
from engine import AtlasEngine
from models import AthleteBiometrics
import json

def test_synthesis():
    # Ensure PROJECT_ID is set
    project_id = os.getenv("PROJECT_ID")
    if not project_id:
        print("Error: PROJECT_ID not set in environment.")
        return

    print(f"Starting re-baseline test with project: {project_id}")
    try:
        engine = AtlasEngine()
        
        # '198cm athlete'
        test_user = AthleteBiometrics(
            athlete_id=999,
            name="Test Athlete",
            height_cm=198.0,
            weight_kg=95.0,
            wingspan_cm=205.0,
            sport="Basketball",
            year=2024,
            is_paralympic=False
        )
        
        print("Executing biometric synthesis...")
        result = engine.generate_insight(test_user)
        
        print("\n--- Synthesis Result (200 OK equivalent) ---")
        print(f"System Node: {result.system_node}")
        print(f"Archetype: {result.archetype_match.archetype_name}")
        print(f"Similarity Score: {result.similarity_score}%")
        print(f"Insight: {result.atlas_insight.insight_text}")
        
    except Exception as e:
        print(f"CRITICAL ERROR during synthesis: {e}")

if __name__ == "__main__":
    test_synthesis()
