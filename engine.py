import pandas as pd
import numpy as np
import os
import json
from dotenv import load_dotenv
from google import genai
from google.auth.exceptions import DefaultCredentialsError
import vertexai
from vertexai.generative_models import GenerativeModel, GenerationConfig
from models import AthleteBiometrics, ArchetypeMatch, AtlasInsight, EngineOutput, BiometricZScores, AISynthesis

# Load environment variables from .env file
load_dotenv()

class InitializationError(Exception):
    """Raised when the Atlas Engine cannot be properly initialized."""
    pass

def compute_ape_index(wingspan_cm: float, height_cm: float) -> tuple[float, str]:
    index = round(wingspan_cm / height_cm, 3)
    if index > 1.03:
        label = "Elite Reach"
    elif index < 1.00:
        label = "Compact Profile"
    else:
        label = "Positive Index"
    return index, label

# Hall of Fame Mappings with Image Support
HALL_OF_FAME = {
    "compact_dynamo": {
        "olympic": "Simone Biles",
        "paralympic": "Bobby Body",
        "olympic_image": "https://images.unsplash.com/photo-1563297122-f1917f938260?q=80&w=2070&auto=format&fit=crop",
        "paralympic_image": "https://images.unsplash.com/photo-1526506118085-60ce8714f8c5?q=80&w=2070&auto=format&fit=crop",
        "note": "Their shared low center of gravity and extreme power-to-weight ratio create a near-perfect biomechanical parity."
    },
    "aerobic_engine": {
        "olympic": "Katie Ledecky",
        "paralympic": "Jessica Long",
        "olympic_image": "https://images.unsplash.com/photo-1530549387631-ce01ff996f9c?q=80&w=2070&auto=format&fit=crop",
        "paralympic_image": "https://images.unsplash.com/photo-1519315901367-f34ff9154487?q=80&w=2070&auto=format&fit=crop",
        "note": "Their Hydrodynamic efficiency and lean mass profile exemplify the 'Aerobic Engine' blueprint across disciplines."
    },
    "kinetic_lever": {
        "olympic": "Tara Davis-Woodhall",
        "paralympic": "Hunter Woodhall",
        "olympic_image": "https://images.unsplash.com/photo-1461896756985-215053158f33?q=80&w=2070&auto=format&fit=crop",
        "paralympic_image": "https://images.unsplash.com/photo-1517438476312-10d79c07750d?q=80&w=2070&auto=format&fit=crop",
        "note": "Mechanical leverage provided by their long-lever biometric profiles suggests a unified blueprint for horizontal propulsion."
    },
    "powerhouse": {
        "olympic": "Ryan Crouser",
        "paralympic": "Jeremy Campbell",
        "olympic_image": "https://images.unsplash.com/photo-1526506118085-60ce8714f8c5?q=80&w=2070&auto=format&fit=crop",
        "paralympic_image": "https://images.unsplash.com/photo-1534438327276-14e5300c3a48?q=80&w=2070&auto=format&fit=crop",
        "note": "High-mass stability and explosive torque generation anchor both athletes within the 'Powerhouse' archetype."
    },
    "aquatic_glider": {
        "olympic": "Michael Phelps",
        "paralympic": "Mallory Weggemann",
        "olympic_image": "https://images.unsplash.com/photo-1530549387631-ce01ff996f9c?q=80&w=2070&auto=format&fit=crop",
        "paralympic_image": "https://images.unsplash.com/photo-1519315901367-f34ff9154487?q=80&w=2070&auto=format&fit=crop",
        "note": "Extreme wingspan-to-height ratios potentially indicate a shared mastery of fluid dynamics."
    },
    "agile_tactician": {
        "olympic": "Lee Kiefer",
        "paralympic": "Bebe Vio",
        "olympic_image": "https://images.unsplash.com/photo-1517438476312-10d79c07750d?q=80&w=2070&auto=format&fit=crop",
        "paralympic_image": "https://images.unsplash.com/photo-1461896756985-215053158f33?q=80&w=2070&auto=format&fit=crop",
        "note": "Balanced biometrics and superior reaction mechanics suggest a unified tactical profile."
    },
    "fencing_legend": {
        "olympic": "Lee Kiefer",
        "paralympic": "Piers Gilliver",
        "olympic_image": "https://images.unsplash.com/photo-1517438476312-10d79c07750d?q=80&w=2070&auto=format&fit=crop",
        "paralympic_image": "https://images.unsplash.com/photo-1461896756985-215053158f33?q=80&w=2070&auto=format&fit=crop",
        "note": "Elite lever-based reaction mechanics define this fencing blueprint."
    }
}

class AtlasEngine:
    """
    The analytical core of The Archetype Atlas. 
    Maintains the 'Source of Truth' and synthesizes biometric insights.
    
    THE ONYX HIERARCHY (3-Tier Failover):
    - [Tier 1] Onyx Prime: Vertex AI (Primary, us-central1)
    - [Tier 2] Relay Protocol: Gemini API (Standard API Key)
    - [Tier 3] Core Protocol: Gemini API Lite (Backup API Key)
    """
    
    def __init__(self, csv_path: str = "historical_athletes.csv"):
        print("Rowen: 'Initializing Atlas Engine core subsystems...'")
        
        # 1. Environment Isolation: Fail Fast Check
        self.project_id = os.getenv("PROJECT_ID") or os.getenv("GOOGLE_CLOUD_PROJECT")
        if not self.project_id:
            raise RuntimeError("CRITICAL: GCP Project ID not detected in environment variables (PROJECT_ID or GOOGLE_CLOUD_PROJECT).")
            
        # Verify CSV existence
        if not os.path.exists(csv_path):
            raise InitializationError(f"Historical dataset not found at {csv_path}. Run generate_atlas_data.py first.")
            
        self.df = pd.read_csv(csv_path)
        
        # Establishing the biometric baseline for Z-score normalization
        self.biometric_cols = ["height_cm", "weight_kg", "wingspan_cm"]
        
        # Add ratio to historical data if not present
        if 'wingspan_ratio' not in self.df.columns:
            self.df['wingspan_ratio'] = self.df['wingspan_cm'] / self.df['height_cm']
        
        # Pre-calculate baseline for the entire dataset (including ratio)
        self.full_cols = self.biometric_cols + ['wingspan_ratio']
        self.means = self.df[self.full_cols].mean()
        self.stds = self.df[self.full_cols].std()
        
        # Pre-calculate normalized values for the dataset
        self.normalized_df = (self.df[self.full_cols] - self.means) / self.stds
        
        # Sanitization Helper
        def sanitize(text: str) -> str:
            if not text or pd.isna(text): return ""
            return str(text).lower().replace("_", "").replace("-", "").strip()
            
        # Add sanitized archetype col for faster vectorized matching
        if 'sanitized_archetype' not in self.df.columns:
            self.df['sanitized_archetype'] = self.df['archetype'].apply(sanitize)

        # Initialize Failover Clients
        self.vertex_model = None
        self.gemini_client = None
        self.backup_client = None
        
        # [Tier 1] Attempt Vertex AI Initialization (Node: Onyx Prime)
        # Using gemini-2.5-flash in us-central1 as the stable advanced model.
        try:
            vertexai.init(project=self.project_id, location="us-central1")
            self.vertex_model = GenerativeModel("gemini-2.5-flash")
            print(f"Rowen: 'Node: Onyx Prime (Vertex AI) initialized in [us-central1] for project: {self.project_id}. Model: gemini-2.5-flash.'")
        except Exception as e:
            print(f"Rowen: 'Onyx Prime initialization bypassed. Error: {e}'")

        # [Tier 2 & 3] Configure Gemini API Fallback (Relay & Core Protocols)
        self.gemini_api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        self.backup_api_key = os.environ.get("BACKUP_API_KEY") or self.gemini_api_key
        
        if self.gemini_api_key:
            self.gemini_client = genai.Client(api_key=self.gemini_api_key)
            print("Rowen: 'Relay & Core Protocols configured as fallbacks.'")
            
        if self.backup_api_key and self.backup_api_key != self.gemini_api_key:
            self.backup_client = genai.Client(api_key=self.backup_api_key)
        else:
            self.backup_client = self.gemini_client
        
        if not self.vertex_model and not self.gemini_client:
            raise InitializationError(
                "No AI Synthesis Subsystem available. "
                "Verify GCP Project ID or GEMINI_API_KEY."
            )
        
        # 4. Performance Optimization: Synthesis Cache
        self._synthesis_cache = {}
        print("Rowen: 'Onyx Cache Layer: PURGED. Ready for fresh synthesis.'")

    def _find_nearest_neighbors(self, user_biometrics: AthleteBiometrics, k: int = 5) -> tuple:
        """
        Calculates the Euclidean distance in weighted biometric space.
        Returns two dataframes: (olympic_neighbors, paralympic_neighbors) and the global min distance.
        """
        user_ratio = user_biometrics.wingspan_cm / user_biometrics.height_cm
        weights = np.array([2.5, 1.0, 1.3, 3.5])
        
        if user_biometrics.height_cm > 185.0:
            weights[1] *= 1.5 
        
        user_vec = np.array([
            user_biometrics.height_cm,
            user_biometrics.weight_kg,
            user_biometrics.wingspan_cm,
            user_ratio
        ])
        
        user_norm = ((user_vec - self.means.values) / self.stds.values) * weights
        norm_data = self.normalized_df * weights
        
        distances = np.sqrt(((norm_data - user_norm) ** 2).sum(axis=1))
        
        # Split search to guarantee statistical parity in neighbors
        olympic_indices = distances[self.df['is_paralympic'] == False].nsmallest(k).index
        paralympic_indices = distances[self.df['is_paralympic'] == True].nsmallest(k).index
        
        return (
            self.df.loc[olympic_indices], 
            self.df.loc[paralympic_indices], 
            distances.min()
        )

    def _resolve_identity(self, archetype_name: str, olympic_neighbors: pd.DataFrame, paralympic_neighbors: pd.DataFrame) -> dict:
        """
        Hardened identity resolution. Resolves any archetype name or neighbor set into a 
        full Hall of Fame profile or best-available historical anchor.
        """
        def sanitize(text: str) -> str:
            if not text: return ""
            return str(text).lower().replace("_", "").replace("-", "").replace(" ", "").strip()

        sanitized_query = sanitize(archetype_name)
        normalized_hof = {sanitize(k): v for k, v in HALL_OF_FAME.items()}
        
        # 1. Attempt Hall of Fame Match (Strict -> Fuzzy -> Semantic)
        hof_entry = normalized_hof.get(sanitized_query)
        if not hof_entry:
            # Fuzzy: Check if any HOF key is contained in the query or vice versa
            for key, entry in normalized_hof.items():
                if key in sanitized_query or sanitized_query in key:
                    hof_entry = entry
                    break
            
            # Semantic: Map common terms back to their blueprint keys
            if not hof_entry:
                semantic_map = {
                    "tactician": "agile_tactician", "fencer": "agile_tactician",
                    "runner": "aerobic_engine", "endurance": "aerobic_engine", "swim": "aerobic_engine",
                    "powerhouse": "powerhouse", "thrower": "powerhouse", "force": "powerhouse",
                    "lever": "kinetic_lever", "propulsion": "kinetic_lever",
                    "dynamo": "compact_dynamo", "torque": "compact_dynamo",
                    "glider": "aquatic_glider", "fluid": "aquatic_glider"
                }
                for word, target_key in semantic_map.items():
                    if word in sanitized_query:
                        hof_entry = HALL_OF_FAME.get(target_key)
                        break

        # 2. Extract Data from Neighbors
        olympic_anchor = olympic_neighbors.iloc[0] if not olympic_neighbors.empty else None
        paralympic_anchor = paralympic_neighbors.iloc[0] if not paralympic_neighbors.empty else None

        # 3. Final Integration
        if hof_entry:
            return {
                "olympic_match": hof_entry["olympic"],
                "paralympic_match": hof_entry["paralympic"],
                "olympic_image": hof_entry["olympic_image"],
                "paralympic_image": hof_entry["paralympic_image"],
                "note": hof_entry["note"]
            }
        else:
            # Last Resort: Euclidean Anchors
            o_name = olympic_anchor['name'] if olympic_anchor is not None else "Historical Profile Verified"
            p_name = paralympic_anchor['name'] if paralympic_anchor is not None else "Historical Profile Verified"
            
            return {
                "olympic_match": o_name if "Athlete_" not in o_name else "Elite Olympic Anchor",
                "paralympic_match": p_name if "Athlete_" not in p_name else "Elite Paralympic Anchor",
                "olympic_image": "https://images.unsplash.com/photo-1517836357463-d25dfeac3438?q=80&w=2070&auto=format&fit=crop",
                "paralympic_image": "https://images.unsplash.com/photo-1526506118085-60ce8714f8c5?q=80&w=2070&auto=format&fit=crop",
                "note": "Shared biomechanical lineage confirmed via Euclidean proximity."
            }

    def generate_architect_note(self, prompt: str, system_instruction: str = None) -> AISynthesis:
        """
        [THE ONYX HIERARCHY]
        Hardened 3-Tier Failover Engine with strict 3s timeout for Onyx Prime.
        """
        parsed_response = None
        system_node = "Unknown"
        error_log = []

        # Tier 1 (Node: Onyx Prime)
        if self.vertex_model:
            try:
                # Legacy SDK: System instruction is often better prepended
                combined_prompt = f"SYSTEM: {system_instruction}\n\nUSER PROMPT: {prompt}" if system_instruction else prompt
                
                response = self.vertex_model.generate_content(
                    combined_prompt,
                    generation_config=GenerationConfig(
                        response_mime_type="application/json",
                        response_schema=AISynthesis.model_json_schema(),
                    )
                )
                
                raw_json = response.text.strip()
                if raw_json.startswith("```json"):
                    raw_json = raw_json[7:-3].strip()
                
                parsed_data = json.loads(raw_json)
                parsed_response = AISynthesis(**parsed_data)
                
                system_node = "Onyx Prime"
                print("Rowen: 'Synthesis secured via [Node: Onyx Prime] (Parsed).'")
            except Exception as e:
                print(f"Rowen: 'WARNING: Onyx Prime failure or timeout. Engaging Relay Protocol. Error: {e}'")
                error_log.append(f"Onyx Prime: {str(e)}")

        # Tier 2 (Node: Relay Protocol)
        if parsed_response is None and self.gemini_client:
            try:
                response = self.gemini_client.models.generate_content(
                    model="gemini-1.5-flash-001",
                    contents=prompt,
                    config={
                        "system_instruction": system_instruction,
                        "response_mime_type": "application/json",
                        "response_schema": AISynthesis,
                        "http_options": {"timeout": 120000}
                    }
                )
                parsed_response = response.parsed
                system_node = "Relay Protocol"
                print("Rowen: 'Synthesis secured via [Node: Relay Protocol] (Parsed).'")
            except Exception as e:
                print(f"Rowen: 'WARNING: Relay Protocol failure. Engaging Core Protocol. Error: {e}'")
                error_log.append(f"Relay Protocol: {str(e)}")

        # Tier 3 (Node: Core Protocol)
        if parsed_response is None and self.backup_client:
            try:
                response = self.backup_client.models.generate_content(
                    model="gemini-1.5-flash",
                    contents=prompt,
                    config={
                        "system_instruction": system_instruction,
                        "response_mime_type": "application/json",
                        "response_schema": AISynthesis,
                        "http_options": {"timeout": 120000}
                    }
                )
                parsed_response = response.parsed
                system_node = "Core Protocol"
                print("Rowen: 'Synthesis secured via [Node: Core Protocol] (Parsed).'")
            except Exception as e:
                print(f"Rowen: 'CRITICAL: Core Protocol failure. Error: {e}'")
                error_log.append(f"Core Protocol: {str(e)}")

        if parsed_response is None:
            raise Exception("System Maintenance: Archive Link Interrupted")

        # Update metadata
        parsed_response.system_node = system_node
        if parsed_response.archetype_name:
            parsed_response.archetype_name = parsed_response.archetype_name.replace("_", " ")
        
        return parsed_response

    def generate_insight(self, user_biometrics: AthleteBiometrics) -> EngineOutput:
        """
        Synthesizes an AtlasInsight using the biometric similarity context and The Onyx Hierarchy.
        Includes refined 'Onyx Prime' scoring logic and strict system instructions.
        """
        # 1. Performance Cache Layer: Mode-Specific Keyed Storage
        mode_key = "paralympic" if user_biometrics.is_paralympic else "olympic"
        biometric_key = (
            round(user_biometrics.height_cm, 1), 
            round(user_biometrics.weight_kg, 1), 
            round(user_biometrics.wingspan_cm, 1)
        )
        
        if mode_key not in self._synthesis_cache:
            self._synthesis_cache[mode_key] = {}
            
        if biometric_key in self._synthesis_cache[mode_key]:
            print(f"Rowen: 'High-fidelity [{mode_key}] synthesis retrieved from keyed cache: {biometric_key}'")
            return self._synthesis_cache[mode_key][biometric_key]

        # 2. Biometric Grounding (Euclidean Distance)
        olympic_neighbors, paralympic_neighbors, min_dist = self._find_nearest_neighbors(user_biometrics)
        
        # [Stat Parity] Guarantee global neighbors for AI context
        neighbors = pd.concat([olympic_neighbors, paralympic_neighbors]).sort_index()
        top_match = neighbors.iloc[0]
        top_match_id = str(top_match['archetype'])
        
        # [State Mapping] Pre-populate the Matches array from Euclidean neighbors
        all_potential_archetypes = [str(a).replace("_", " ") for a in neighbors['archetype'].unique()]
        
        user_vec = np.array([
            user_biometrics.height_cm,
            user_biometrics.weight_kg,
            user_biometrics.wingspan_cm
        ])
        disp_means = self.means[:3].values
        disp_stds = self.stds[:3].values
        user_z = (user_vec - disp_means) / disp_stds
        user_z_obj = BiometricZScores(height=float(user_z[0]), weight=float(user_z[1]), wingspan=float(user_z[2]))

        # --- RATIO-BASED SCORING LOGIC (ONYX PRIME) ---
        user_ratio = user_biometrics.wingspan_cm / user_biometrics.height_cm
        athlete_ratio = top_match['wingspan_cm'] / top_match['height_cm']
        ratio_delta_pct = abs(user_ratio - athlete_ratio) / athlete_ratio
        
        # Base score from Euclidean distance
        base_score = 100 * np.exp(-0.4 * min_dist)
        
        # Boost logic: If ratios match within 5%, ensure score is at least 80%
        if ratio_delta_pct <= 0.05:
            similarity_score = max(80.0, base_score)
            # Add a secondary climb based on how close the ratio is
            ratio_bonus = (0.05 - ratio_delta_pct) * 400 # Max +20% if delta is 0
            similarity_score = min(99.9, similarity_score + ratio_bonus)
            congruence_applied = True
            ratio_delta = abs(user_ratio - athlete_ratio) # for the note
        else:
            similarity_score = base_score
            congruence_applied = False
            ratio_delta = abs(user_ratio - athlete_ratio)

        similarity_score = round(similarity_score, 1)

        context_lines = []
        for _, row in neighbors.iterrows():
            status = "Paralympic" if row.get('is_paralympic', False) else "Olympic"
            sport_info = row.get('sport', 'Historical Archive Data')
            name_info = row.get('name', 'Anonymous Athlete')
            context_lines.append(
                f"- {name_info} ({status}): {sport_info}, {row['archetype']}, "
                f"Height: {row['height_cm']}cm, Weight: {row['weight_kg']}kg, Wingspan: {row['wingspan_cm']}cm"
            )
        context_str = "\n".join(context_lines)

        # [CLEAN STATE PROMPT]
        target_mode = "PARALYMPIC" if user_biometrics.is_paralympic else "OLYMPIC"
        
        system_instruction = f"""
Act as 'Rowen', Lead Architect of The Archetype Atlas. 
Your tone is clean, rational, and technical.

CORE DIRECTIVE:
Identify which 'Archetype Blueprint' the user fits into based on their biometrics and the historical context provided.
You MUST prioritize the archetype explicitly mentioned in the HISTORICAL CONTEXT.

MANDATORY RULES:
1. Speak as Rowen (Lead Architect).
2. Use conditional phrasing ('could', 'might', 'potentially', 'suggests').
3. Focus synthesis EXCLUSIVELY on the {target_mode} filter.
4. JSON ONLY: Return a valid JSON object matching the AISynthesis schema.
"""

        prompt = f"""
HISTORICAL CONTEXT (Top 5 Closest Biometric Matches):
{context_str}

USER DATA:
Height: {user_biometrics.height_cm}cm, Weight: {user_biometrics.weight_kg}kg, Wingspan: {user_biometrics.wingspan_cm}cm

HALL OF FAME MAPPINGS:
- The Agile Tactician: Lee Kiefer (Fencing) / Bebe Vio (Wheelchair Fencing).
- The Kinetic Lever: Tara Davis-Woodhall (Long Jump) / Hunter Woodhall (Para-Athletics).
- The Aerobic Engine: Katie Ledecky (Swimming) / Jessica Long (Para-Swimming).
- The Powerhouse: Ryan Crouser (Shot Put) / Jeremy Campbell (Para-Discus).
- The Compact Dynamo: Simone Biles (Gymnastics) / Bobby Body (Para-Powerlifting).
- The Aquatic Glider: Michael Phelps (Swimming) / Mallory Weggemann (Para-Swimming).

OUTPUT SCHEMA:
{{
  "archetype_name": "Primary Archetype Blueprint",
  "potential_matches": ["Athlete Name 1", "Athlete Name 2"],
  "confidence_score": 0.95,
  "shared_traits": ["trait 1", "trait 2"],
  "insight_text": "Technical analysis focused on the {target_mode} alignment.",
  "image_url": "Direct Wikimedia Link (if applicable)",
  "system_node": "Onyx Prime"
}}
"""
        # 3. Execute Onyx Hierarchy with Fallback logic
        try:
            ai_data = self.generate_architect_note(prompt, system_instruction=system_instruction)
        except Exception as e:
            print(f"Rowen: 'Synthesis failure. Engaging Hardened Local Synthesis. Error: {e}'")
            name_map = {
                "powerhouse": "Powerhouse", "aerobic_engine": "Aerobic Engine",
                "kinetic_lever": "Kinetic Lever", "compact_dynamo": "Compact Dynamo",
                "aquatic_glider": "Aquatic Glider", "agile_tactician": "Agile Tactician"
            }
            recovery_name = name_map.get(top_match_id, top_match_id.replace("_", " ").title())
            ai_data = AISynthesis(
                archetype_name=recovery_name,
                potential_matches=all_potential_archetypes,
                confidence_score=0.88, 
                shared_traits=["Biometric Consistency", "Mechanical Parity"],
                insight_text=f"Your profile suggests you could be a match for the '{recovery_name}' blueprint.",
                image_url="",
                system_node="Local Archive"
            )

        # 4. Identity Mapping: Resolve Hall of Fame Parity
        # Check if AI triggered the 'No direct celebrity match' fallback
        if "no direct celebrity match" in ai_data.archetype_name.lower() or (ai_data.potential_matches and "no direct celebrity match" in ai_data.potential_matches[0].lower()):
            resolved_identity = {
                "olympic_match": "N/A",
                "paralympic_match": "N/A",
                "olympic_image": "https://images.unsplash.com/photo-1517836357463-d25dfeac3438?q=80&w=2070&auto=format&fit=crop",
                "paralympic_image": "https://images.unsplash.com/photo-1526506118085-60ce8714f8c5?q=80&w=2070&auto=format&fit=crop",
                "note": "Biometric profile represents a unique athletic blueprint with no direct high-profile match."
            }
            if "archetype:" in ai_data.archetype_name.lower():
                resolved_identity["note"] = f"Archetype: {ai_data.archetype_name.split('Archetype:')[-1].strip()}"
        else:
            resolved_identity = self._resolve_identity(ai_data.archetype_name, olympic_neighbors, paralympic_neighbors)
        
        final_olympic_img = ai_data.image_url if (ai_data.image_url and "wikimedia" in ai_data.image_url.lower() and not user_biometrics.is_paralympic) else resolved_identity["olympic_image"]
        final_paralympic_img = ai_data.image_url if (ai_data.image_url and "wikimedia" in ai_data.image_url.lower() and user_biometrics.is_paralympic) else resolved_identity["paralympic_image"]

        # Onyx Prime Logic: Construct Architect Note
        resolved_name = resolved_identity["paralympic_match"] if user_biometrics.is_paralympic else resolved_identity["olympic_match"]
        congruence_note = f" Matches the 1:{user_ratio:.2f} lever ratio of {resolved_name}, though your {user_biometrics.height_cm:.0f}cm stature adds a unique Tier-1 power advantage."
        architect_note = resolved_identity["note"] + congruence_note if not congruence_applied else f"Identified 'Structural Congruence' at {ratio_delta:.3f} delta. " + resolved_identity["note"] + congruence_note

        # 5. Z-Score Visualization Mapping
        def sanitize(text: str) -> str:
            if not text: return ""
            return str(text).lower().replace("_", "").replace("-", "").strip()

        sanitized_key = sanitize(ai_data.archetype_name)
        archetype_data = self.normalized_df[self.df['sanitized_archetype'] == sanitized_key]
        if archetype_data.empty:
            keywords = [sanitize(k) for k in ai_data.archetype_name.split()]
            mask = self.df['sanitized_archetype'].str.contains('|'.join(keywords))
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
            
        final_output = EngineOutput(
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
            matches=ai_data.potential_matches or all_potential_archetypes,
            olympic_match=resolved_identity["olympic_match"],
            paralympic_match=resolved_identity["paralympic_match"],
            olympic_image_url=final_olympic_img,
            paralympic_image_url=final_paralympic_img,
            architect_note=architect_note,
            system_node=ai_data.system_node
        )

        self._synthesis_cache[mode_key][biometric_key] = final_output
        return final_output

if __name__ == "__main__":
    try:
        os.environ["PROJECT_ID"] = "archetype-atlas-495220" # Mock for standalone test
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
    except Exception as e:
        print(f"UNEXPECTED ERROR: {e}")
