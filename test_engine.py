from engine import AtlasEngine
from models import AthleteBiometrics
import os

def run_atlas_test():
    print("Rowen: 'Commencing live-fire engine test...'")
    
    try:
        engine = AtlasEngine()
        
        # Test Case 1: The Aerobic Engine Profile (Marathon Runner type)
        aerobic_profile = AthleteBiometrics(
            athlete_id=1,
            name="Endurance Test",
            height_cm=172.0,
            weight_kg=58.0,
            wingspan_cm=174.0,
            sport="TBD",
            year=2026,
            is_paralympic=False
        )
        
        # Test Case 2: The Powerhouse Profile (Shotputter type)
        power_profile = AthleteBiometrics(
            athlete_id=2,
            name="Power Test",
            height_cm=198.0,
            weight_kg=125.0,
            wingspan_cm=202.0,
            sport="TBD",
            year=2026,
            is_paralympic=False
        )
        
        test_cases = [
            ("Aerobic Test", aerobic_profile),
            ("Power Test", power_profile)
        ]
        
        for label, profile in test_cases:
            print(f"\n--- Testing {label} ---")
            result = engine.generate_insight(profile)
            print(f"Matched Archetype: {result.archetype_match.archetype_name}")
            print(f"Confidence: {result.archetype_match.confidence_score}")
            print(f"Rowen's Insight: {result.atlas_insight.insight_text}")
            
    except Exception as e:
        print(f"Rowen: 'System alert - Analysis interrupted.' Error: {e}")

if __name__ == "__main__":
    run_atlas_test()
