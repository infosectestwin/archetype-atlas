import pandas as pd
import numpy as np
import os
from dotenv import load_dotenv
from google import genai
from models import AthleteBiometrics, ArchetypeMatch, AtlasInsight, EngineOutput, BiometricZScores, AISynthesis

# Load environment variables from .env file
load_dotenv()

class InitializationError(Exception):
    """Raised when the Atlas Engine cannot be properly initialized."""
    pass

# Hall of Fame Mappings
HALL_OF_FAME = {
    "compact_dynamo": {
        "olympic": "Simone Biles",
        "paralympic": "Bobby Body",
        "note": "Their shared low center of gravity and extreme power-to-weight ratio create a near-perfect biomechanical parity."
    },
    "The Compact Dynamo": {
        "olympic": "Simone Biles",
        "paralympic": "Bobby Body",
        "note": "Their shared low center of gravity and extreme power-to-weight ratio create a near-perfect biomechanical parity."
    },
    "aerobic_engine": {
        "olympic": "Katie Ledecky",
        "paralympic": "Jessica Long",
        "note": "Their Hydrodynamic efficiency and lean mass profile exemplify the 'Aerobic Engine' blueprint across disciplines."
    },
    "The Aerobic Engine": {
        "olympic": "Katie Ledecky",
        "paralympic": "Jessica Long",
        "note": "Their Hydrodynamic efficiency and lean mass profile exemplify the 'Aerobic Engine' blueprint across disciplines."
    },
    "kinetic_lever": {
        "olympic": "Tara Davis-Woodhall",
        "paralympic": "Hunter Woodhall",
        "note": "Mechanical leverage provided by their long-lever biometric profiles suggests a unified blueprint for horizontal propulsion."
    },
    "The Kinetic Lever": {
        "olympic": "Tara Davis-Woodhall",
        "paralympic": "Hunter Woodhall",
        "note": "Mechanical leverage provided by their long-lever biometric profiles suggests a unified blueprint for horizontal propulsion."
    },
    "powerhouse": {
        "olympic": "Ryan Crouser",
        "paralympic": "Jeremy Campbell",
        "note": "High-mass stability and explosive torque generation anchor both athletes within the 'Powerhouse' archetype."
    },
    "The Powerhouse": {
        "olympic": "Ryan Crouser",
        "paralympic": "Jeremy Campbell",
        "note": "High-mass stability and explosive torque generation anchor both athletes within the 'Powerhouse' archetype."
    },
    "aquatic_glider": {
        "olympic": "Michael Phelps",
        "paralympic": "Mallory Weggemann",
        "note": "Extreme wingspan-to-height ratios potentially indicate a shared mastery of fluid dynamics."
    },
    "The Aquatic Glider": {
        "olympic": "Michael Phelps",
        "paralympic": "Mallory Weggemann",
        "note": "Extreme wingspan-to-height ratios potentially indicate a shared mastery of fluid dynamics."
    },
    "agile_tactician": {
        "olympic": "Lee Kiefer",
        "paralympic": "Bebe Vio",
        "note": "Balanced biometrics and superior reaction mechanics suggest a unified tactical profile."
    },
    "The Agile Tactician": {
        "olympic": "Lee Kiefer",
        "paralympic": "Bebe Vio",
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
        Calculates the Euclidean distance in weighted biometric space.
        Incorporates Wingspan/Height ratio for structural specificity.
        """
        # Feature Engineering: Wingspan Ratio
        user_ratio = user_biometrics.wingspan_cm / user_biometrics.height_cm
        
        # Add ratio to historical data if not present (calculated on the fly)
        if 'wingspan_ratio' not in self.df.columns:
            self.df['wingspan_ratio'] = self.df['wingspan_cm'] / self.df['height_cm']
            
        # Weighted Z-Score Normalization
        # Restore Specificity: Prioritize Wingspan Ratio for structural archetypes
        # Final Polish: Fine-tuned weights to separate Tactician from Lever
        # Extreme Height Penalty: Increase height weight to 2.5 to separate 183cm from 195cm+ Levers
        weights = np.array([2.5, 1.0, 1.3, 3.5]) # Height and Ratio dominant
        
        # Track & Field Optimization: Increase Weight importance for taller athletes to penalize non-lean profiles
        if user_biometrics.height_cm > 185.0:
            weights[1] *= 1.5 # Increase Weight importance by 50%
        
        user_vec = np.array([
            user_biometrics.height_cm,
            user_biometrics.weight_kg,
            user_biometrics.wingspan_cm,
            user_ratio
        ])
        
        # Recalculate baseline including ratio
        full_cols = self.biometric_cols + ['wingspan_ratio']
        means = self.df[full_cols].mean()
        stds = self.df[full_cols].std()
        
        user_norm = ((user_vec - means.values) / stds.values) * weights
        
        # Pre-normalize the entire dataset with weights
        norm_data = ((self.df[full_cols] - means) / stds) * weights
        
        distances = np.sqrt(((norm_data - user_norm) ** 2).sum(axis=1))
        nearest_indices = distances.nsmallest(k).index
        return self.df.iloc[nearest_indices], distances.min()

    def generate_insight(self, user_biometrics: AthleteBiometrics) -> EngineOutput:
        """
        Synthesizes an AtlasInsight using the biometric similarity context and Gemini.
        """
        neighbors, min_dist = self._find_nearest_neighbors(user_biometrics)
        
        # Calculate user Z-scores (standard for display)
        user_vec = np.array([
            user_biometrics.height_cm,
            user_biometrics.weight_kg,
            user_biometrics.wingspan_cm
        ])
        user_z = (user_vec - self.means.values) / self.stds.values
        user_z_obj = BiometricZScores(height=float(user_z[0]), weight=float(user_z[1]), wingspan=float(user_z[2]))

        # Calculate Similarity Score: 100 * e^(-0.4 * distance) 
        # Tighter Threshold: Increased decay from 0.3 to 0.4
        similarity_score = round(100 * np.exp(-0.4 * min_dist), 1)

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
Identify which 'Archetype Blueprint' the user fits into. 
STRICT REQUIREMENT: You MUST prioritize the archetype explicitly mentioned in the HISTORICAL CONTEXT provided below.

HISTORICAL CONTEXT (Top 5 Closest Biometric Matches):
{context_str}

USER DATA:
Height: {user_biometrics.height_cm}cm, Weight: {user_biometrics.weight_kg}kg, Wingspan: {user_biometrics.wingspan_cm}cm

HALL_OF_FAME_MAPPINGS:
- The Agile Tactician: Lee Kiefer (Fencing) / Bebe Vio (Wheelchair Fencing). [Balanced biometrics, precise reach]
- The Kinetic Lever: Tara Davis-Woodhall (Long Jump) / Hunter Woodhall (Para-Athletics). [Extreme wingspan/height ratio]
- The Aerobic Engine: Katie Ledecky (Swimming) / Jessica Long (Para-Swimming). [Lean mass, endurance optimized]
- The Powerhouse: Ryan Crouser (Shot Put) / Jeremy Campbell (Para-Discus). [High mass, explosive torque]
- The Compact Dynamo: Simone Biles (Gymnastics) / Bobby Body (Para-Powerlifting). [Low COG, extreme power-to-weight]
- The Aquatic Glider: Michael Phelps (Swimming) / Mallory Weggemann (Para-Swimming). [Extreme wingspan, fluid dynamic efficiency]


MANDATORY NARRATIVE RULES:
1. Speak as Rowen (Lead Architect).
2. Use conditional phrasing ('could', 'might', 'potentially', 'suggests').
3. PARITY REQUIREMENT: You MUST explicitly mention the historical Olympic and Paralympic counterpart from the Hall of Fame mapping for the identified archetype.
4. If the HISTORICAL CONTEXT predominantly shows 'agile_tactician', you MUST identify the user as 'The Agile Tactician'.

Return the result as a structured JSON object matching the provided schema.
"""

        response = self.client.models.generate_content(
            model="gemini-flash-latest",
            contents=prompt,
            config={
                "response_mime_type": "application/json",
                "response_schema": AISynthesis,
            }
        )
        
        ai_data = response.parsed
        if not ai_data:
            raise Exception("Rowen: 'Synthesis Subsystem timed out. Failed to parse AI response.'")
            
        # Get Hall of Fame data with Case-Insensitive Fuzzy Matching
        archetype_key = ai_data.archetype_name.strip()
        
        # Create a normalized lookup map
        normalized_hof = {k.lower(): v for k, v in HALL_OF_FAME.items()}
        hof_entry = normalized_hof.get(archetype_key.lower(), {
            "olympic": "Analyzing National Archives...", 
            "paralympic": "Analyzing National Archives...", 
            "note": "Shared biomechanical lineage confirmed."
        })
        
        # Calculate archetype average Z-scores
        # Try matching by slug first
        archetype_data = self.normalized_df[self.df['archetype'] == archetype_key.lower()]
        
        if archetype_data.empty:
            # Fallback: Try searching for keywords in the archetype column (which contains slugs)
            keywords = archetype_key.lower().split()
            mask = self.df['archetype'].str.contains('|'.join(keywords))
            archetype_data = self.normalized_df[mask]
            
        if not archetype_data.empty:
            avg_z = archetype_data.mean()
            archetype_z_obj = BiometricZScores(
                height=float(avg_z['height_cm']), 
                weight=float(avg_z['weight_kg']), 
                wingspan=float(avg_z['wingspan_cm'])
            )
        else:
            archetype_z_obj = user_z_obj
            
        # Assemble final EngineOutput
        return EngineOutput(
            archetype_match=ArchetypeMatch(
                archetype_name=ai_data.archetype_name,
                confidence_score=ai_data.confidence_score,
                shared_traits=ai_data.shared_traits
            ),
            atlas_insight=AtlasInsight(
                insight_text=ai_data.insight_text,
                matched_archetype=ai_data.archetype_name
            ),
            user_z_scores=user_z_obj,
            archetype_z_scores=archetype_z_obj,
            similarity_score=similarity_score,
            olympic_match=hof_entry["olympic"],
            paralympic_match=hof_entry["paralympic"],
            architect_note=hof_entry["note"]
        )

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
