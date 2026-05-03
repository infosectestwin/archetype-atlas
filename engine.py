import pandas as pd
import numpy as np
import os
from dotenv import load_dotenv
from google import genai
from models import AthleteBiometrics, ArchetypeMatch, AtlasInsight, EngineOutput, BiometricZScores

# Load environment variables from .env file
load_dotenv()

class InitializationError(Exception):
    """Raised when the Atlas Engine cannot be properly initialized."""
    pass

# Hall of Fame Mappings
HALL_OF_FAME = {
    "The Compact Dynamo": {
        "olympic": "Simone Biles (Gymnastics)",
        "paralympic": "Bobby Body (Para-Powerlifting)",
        "note": "Their shared low center of gravity and extreme power-to-weight ratio create a near-perfect biomechanical parity."
    },
    "The Aerobic Engine": {
        "olympic": "Katie Ledecky (Swimming)",
        "paralympic": "Jessica Long (Para-Swimming)",
        "note": "Their Hydrodynamic efficiency and lean mass profile exemplify the 'Aerobic Engine' blueprint across disciplines."
    },
    "The Kinetic Lever": {
        "olympic": "Tara Davis-Woodhall (Long Jump)",
        "paralympic": "Hunter Woodhall (Para-Athletics)",
        "note": "Mechanical leverage provided by their long-lever biometric profiles suggests a unified blueprint for horizontal propulsion."
    },
    "The Powerhouse": {
        "olympic": "Ryan Crouser (Shot Put)",
        "paralympic": "Jeremy Campbell (Para-Discus)",
        "note": "High-mass stability and explosive torque generation anchor both athletes within the 'Powerhouse' archetype."
    },
    "The Aquatic Glider": {
        "olympic": "Michael Phelps (Swimming)",
        "paralympic": "Mallory Weggemann (Para-Swimming)",
        "note": "Extreme wingspan-to-height ratios potentially indicate a shared mastery of fluid dynamics."
    },
    "The Agile Tactician": {
        "olympic": "Lee Kiefer (Fencing)",
        "paralympic": "Bebe Vio (Wheelchair Fencing)",
        "note": "Balanced biometrics and superior reaction mechanics suggest a unified tactical profile."
    }
}

class AtlasEngine:
    """
    The analytical core of The Archetype Atlas. 
    Maintains the 'Source of Truth' and synthesizes biometric insights.
    """
    
    def __init__(self, csv_path: str = "historical_athletes.csv"):
        print("Rowen: 'Initializing Atlas Engine core subsystems...'")
        
        # Verify CSV existence
        if not os.path.exists(csv_path):
            raise InitializationError(f"Historical dataset not found at {csv_path}. Run generate_atlas_data.py first.")
            
        self.df = pd.read_csv(csv_path)
        
        # Establishing the biometric baseline for Z-score normalization
        self.biometric_cols = ["height_cm", "weight_kg", "wingspan_cm"]
        self.means = self.df[self.biometric_cols].mean()
        self.stds = self.df[self.biometric_cols].std()
        
        # Pre-calculate normalized values for the dataset
        self.normalized_df = (self.df[self.biometric_cols] - self.means) / self.stds
        
        # Initialize Gemini Client with strict security check
        api_key = os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            raise InitializationError(
                "GOOGLE_API_KEY is missing. Access to the Synthesis Subsystem is denied. "
                "Please add your key to the .env file in the project root."
            )
            
        self.client = genai.Client(api_key=api_key)

    def _find_nearest_neighbors(self, user_biometrics: AthleteBiometrics, k: int = 5) -> tuple:
        """
        Calculates the Euclidean distance in normalized biometric space.
        Returns (DataFrame of neighbors, closest_distance)
        """
        user_vec = np.array([
            user_biometrics.height_cm,
            user_biometrics.weight_kg,
            user_biometrics.wingspan_cm
        ])
        user_norm = (user_vec - self.means.values) / self.stds.values
        
        distances = np.sqrt(((self.normalized_df - user_norm) ** 2).sum(axis=1))
        nearest_indices = distances.nsmallest(k).index
        return self.df.iloc[nearest_indices], distances.min()

    def generate_insight(self, user_biometrics: AthleteBiometrics) -> EngineOutput:
        """
        Synthesizes an AtlasInsight using the biometric similarity context and Gemini.
        """
        neighbors, min_dist = self._find_nearest_neighbors(user_biometrics)
        
        # Calculate user Z-scores
        user_vec = np.array([
            user_biometrics.height_cm,
            user_biometrics.weight_kg,
            user_biometrics.wingspan_cm
        ])
        user_z = (user_vec - self.means.values) / self.stds.values
        user_z_obj = BiometricZScores(height=float(user_z[0]), weight=float(user_z[1]), wingspan=float(user_z[2]))

        # Calculate Similarity Score: 100 * e^(-0.2 * distance)
        similarity_score = round(100 * np.exp(-0.2 * min_dist), 1)

        context_lines = []
        for _, row in neighbors.iterrows():
            status = "Paralympic" if row['is_paralympic'] else "Olympic"
            context_lines.append(
                f"- {row['name']} ({status}): {row['sport']}, {row['archetype']}, "
                f"Height: {row['height_cm']}cm, Weight: {row['weight_kg']}kg, Wingspan: {row['wingspan_cm']}cm"
            )
        context_str = "\n".join(context_lines)

        prompt = f"""
SYSTEM: You are Rowen, the Lead Architect of 'The Archetype Atlas'. 
Your tone is that of a high-end technical manual from a futuristic training facility: clean, rational, and deeply inspiring.

CORE DIRECTIVE:
Identify which 'Archetype Blueprint' the user fits into based on their biometrics and the historical context provided.

HISTORICAL CONTEXT (Top 5 Matches):
{context_str}

USER DATA:
Height: {user_biometrics.height_cm}cm, Weight: {user_biometrics.weight_kg}kg, Wingspan: {user_biometrics.wingspan_cm}cm

HALL OF FAME MAPPINGS (Prioritize these pairs in your narrative for parity):
- The Compact Dynamo: Simone Biles (Gymnastics) / Bobby Body (Para-Powerlifting).
- The Aerobic Engine: Katie Ledecky (Swimming) / Jessica Long (Para-Swimming).
- The Kinetic Lever: Tara Davis-Woodhall (Long Jump) / Hunter Woodhall (Para-Athletics).
- The Powerhouse: Ryan Crouser (Shot Put) / Jeremy Campbell (Para-Discus).

MANDATORY NARRATIVE RULES:
1. Speak as Rowen (Lead Architect).
2. Use conditional phrasing ('could', 'might', 'potentially', 'suggests').
3. PARITY REQUIREMENT: You MUST explicitly mention the historical Olympic and Paralympic counterpart from the Hall of Fame mapping for the identified archetype.
4. Explain WHY the biometrics align with the chosen archetype.

Return the result as a structured EngineOutput.
"""

        response = self.client.models.generate_content(
            model="gemini-flash-latest",
            contents=prompt,
            config={
                "response_mime_type": "application/json",
                "response_schema": EngineOutput,
            }
        )
        
        output = response.parsed
        
        # Inject metadata
        output.user_z_scores = user_z_obj
        output.similarity_score = similarity_score
        
        # Get Hall of Fame data
        hof_entry = HALL_OF_FAME.get(output.archetype_match.archetype_name, {
            "olympic": "N/A", "paralympic": "N/A", "note": "Shared biomechanical lineage confirmed."
        })
        output.olympic_match = hof_entry["olympic"]
        output.paralympic_match = hof_entry["paralympic"]
        output.architect_note = hof_entry["note"]
        
        # Calculate archetype average Z-scores
        archetype_name = output.archetype_match.archetype_name
        archetype_data = self.normalized_df[self.df['archetype'] == archetype_name]
        if not archetype_data.empty:
            avg_z = archetype_data.mean()
            output.archetype_z_scores = BiometricZScores(
                height=float(avg_z['height_cm']), 
                weight=float(avg_z['weight_kg']), 
                wingspan=float(avg_z['wingspan_cm'])
            )
        else:
            output.archetype_z_scores = user_z_obj
            
        return output

if __name__ == "__main__":
    try:
        engine = AtlasEngine()
        dummy_user = AthleteBiometrics(
            athlete_id=0,
            name="Candidate",
            height_cm=195.0,
            weight_kg=85.0,
            wingspan_cm=205.0,
            sport="TBD",
            year=2026,
            is_paralympic=False
        )
        
        result = engine.generate_insight(dummy_user)
        print("\n--- Synthesis Result ---")
        print(f"Archetype: {result.archetype_match.archetype_name}")
        print(f"Similarity Score: {result.similarity_score}%")
        print(f"Insight: {result.atlas_insight.insight_text}")
        
    except InitializationError as e:
        print(f"SYSTEM FAILURE: {e}")
    except Exception as e:
        print(f"UNEXPECTED ERROR: {e}")
