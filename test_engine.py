from engine import AtlasEngine
from models import AthleteBiometrics
import os

def run_atlas_test():
    print("Rowen: 'Commencing live-fire engine test...'")
    
    try:
        engine = AtlasEngine()
        
        # Test Case 1: The Aerobic Engine Profile (Marathon Runner type)
        # Goal: Matches Katie Ledecky / Jessica Long
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
        # Goal: Matches Ryan Crouser / Jeremy Campbell
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

        # Test Case 3: The Kinetic Lever Profile (High Jumper / Long Jumper type)
        # Goal: Matches Tara Davis-Woodhall / Hunter Woodhall
        lever_profile = AthleteBiometrics(
            athlete_id=3,
            name="Kinetic Test",
            height_cm=195.0,
            weight_kg=85.0,
            wingspan_cm=205.0,
            sport="TBD",
            year=2026,
            is_paralympic=False
        )

        # Test Case 4: The Agile Tactician Profile (Fencer type)
        # Goal: Matches Lee Kiefer / Bebe Vio
        tactician_profile = AthleteBiometrics(
            athlete_id=4,
            name="Agility Test",
            height_cm=175.0,
            weight_kg=70.0,
            wingspan_cm=180.0,
            sport="TBD",
            year=2026,
            is_paralympic=False
        )
        
        test_cases = [
            ("Aerobic Test", aerobic_profile),
            ("Power Test", power_profile),
            ("Kinetic Lever Test", lever_profile),
            ("Agile Tactician Test", tactician_profile)
        ]
        
        for label, profile in test_cases:
            print(f"\n--- Testing {label} ---")
            result = engine.generate_insight(profile)
            print(f"Matched Archetype: {result.archetype_match.archetype_name}")
            print(f"Confidence: {result.archetype_match.confidence_score}")
            print(f"Olympic Match: {result.olympic_match}")
            print(f"Paralympic Match: {result.paralympic_match}")
            print(f"Rowen's Insight: {result.atlas_insight.insight_text[:200]}...")
            
    except Exception as e:
        print(f"Rowen: 'System alert - Analysis interrupted.' Error: {e}")

if __name__ == "__main__":
    run_atlas_test()
