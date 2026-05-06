from pydantic import BaseModel, Field, field_validator
from typing import Optional, List

class AthleteBiometrics(BaseModel):
    athlete_id: int
    name: str
    height_cm: float
    weight_kg: float
    wingspan_cm: float
    classification_code: Optional[str] = None  # None for Olympic, e.g., 'T54' for Paralympic
    sport: str
    year: int
    is_paralympic: bool

class ArchetypeMatch(BaseModel):
    archetype_name: str
    confidence_score: float = Field(..., ge=0, le=1)
    shared_traits: List[str]

class AtlasInsight(BaseModel):
    insight_text: str
    matched_archetype: str

    @field_validator('insight_text')
    @classmethod
    def enforce_conditional_phrasing(cls, v: str) -> str:
        conditional_words = ['could', 'might', 'potentially', 'may', 'suggests', 'likely to']
        if not any(word in v.lower() for word in conditional_words):
            raise ValueError(
                "Lead Architect Rowen demands conditional phrasing! "
                "The insight must include terms like 'could', 'might', or 'potentially'."
            )
        return v

class BiometricZScores(BaseModel):
    height: float
    weight: float
    wingspan: float

class AISynthesis(BaseModel):
    archetype_name: str
    potential_matches: List[str] = Field(default_factory=list)
    confidence_score: float = Field(..., ge=0, le=1)
    shared_traits: List[str]
    insight_text: str
    system_node: str  # Observability: Indicates which node synthesized the result

class EngineOutput(BaseModel):
    archetype_match: ArchetypeMatch
    atlas_insight: AtlasInsight
    user_z_scores: BiometricZScores
    archetype_z_scores: BiometricZScores
    similarity_score: float
    matches: List[str] = Field(default_factory=list) # Full array of potential matches
    olympic_match: str
    paralympic_match: str
    olympic_image_url: str = Field(default="https://images.unsplash.com/photo-1517836357463-d25dfeac3438?q=80&w=2070&auto=format&fit=crop")
    paralympic_image_url: str = Field(default="https://images.unsplash.com/photo-1517836357463-d25dfeac3438?q=80&w=2070&auto=format&fit=crop")
    architect_note: str
    system_node: str # Carried from AISynthesis for UI display
