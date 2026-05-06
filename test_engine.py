from engine import AtlasEngine
from models import AthleteBiometrics
import os

def test_run_atlas_test():
    print("Rowen: 'Commencing high-fidelity biometric validation...'")
    
    try:
        engine = AtlasEngine()
        
        # Profile 1: The Aerobic Engine (Endurance)
        # Target: 160-175cm / 45-62kg
        aerobic_profile = AthleteBiometrics(
            athlete_id=1, name="Endurance_Alpha", height_cm=168.0, weight_kg=55.0, wingspan_cm=170.0,
            sport="TBD", year=2026, is_paralympic=False
        )
        
        # Profile 2: The Powerhouse (Force)
        # Target: 188-215cm / 115-150kg
        power_profile = AthleteBiometrics(
            athlete_id=2, name="Force_Delta", height_cm=200.0, weight_kg=130.0, wingspan_cm=210.0,
            sport="TBD", year=2026, is_paralympic=False
        )

        # Profile 3: The Kinetic Lever (Proportion)
        # Target: 192-210cm / Wingspan 220-240cm (Ratio > 1.15)
        lever_profile = AthleteBiometrics(
            athlete_id=3, name="Lever_Sigma", height_cm=198.0, weight_kg=85.0, wingspan_cm=235.0,
            sport="TBD", year=2026, is_paralympic=False
        )

        # Profile 4: The Agile Tactician (Precision)
        # Target: 181-184cm / 71-75kg (Lock at 183cm)
        tactician_profile = AthleteBiometrics(
            athlete_id=4, name="Precision_Omega", height_cm=183.0, weight_kg=73.0, wingspan_cm=193.0,
            sport="TBD", year=2026, is_paralympic=False
        )
        
        test_cases = [
            ("Aerobic Engine", aerobic_profile),
            ("Powerhouse", power_profile),
            ("Kinetic Lever", lever_profile),
            ("Agile Tactician", tactician_profile)
        ]
        
        for label, profile in test_cases:
            print(f"\n[Validation]: {label}")
            result = engine.generate_insight(profile)
            print(f"Matched: {result.archetype_match.archetype_name}")
            print(f"Similarity: {result.similarity_score}%")
            print(f"Olympic: {result.olympic_match}")
            print(f"Paralympic: {result.paralympic_match}")
            print(f"Rowen's Note: {result.architect_note}")
            
    except Exception as e:
        print(f"Rowen: 'System alert - Analysis interrupted.' Error: {e}")

if __name__ == "__main__":
    test_run_atlas_test()
