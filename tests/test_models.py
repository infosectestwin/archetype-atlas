import pytest
from models import EngineOutput, ArchetypeMatch, AtlasInsight, BiometricZScores

def _minimal_output(**overrides):
    defaults = dict(
        archetype_match=ArchetypeMatch(archetype_name="Test", confidence_score=0.9, shared_traits=[]),
        atlas_insight=AtlasInsight(insight_text="This could be a match.", matched_archetype="Test"),
        user_z_scores=BiometricZScores(height=0.0, weight=0.0, wingspan=0.0),
        archetype_z_scores=BiometricZScores(height=0.0, weight=0.0, wingspan=0.0),
        similarity_score=90.0,
        olympic_match="Olympic Athlete",
        paralympic_match="Paralympic Athlete",
        architect_note="Structural parity confirmed.",
        system_node="Test Node",
    )
    defaults.update(overrides)
    return EngineOutput(**defaults)

def test_ape_index_default():
    output = _minimal_output()
    assert output.ape_index == 1.0

def test_ape_index_label_default():
    output = _minimal_output()
    assert output.ape_index_label == "Positive Index"

def test_paralympic_image_url_default_is_empty():
    output = _minimal_output()
    assert output.paralympic_image_url == ""

def test_olympic_image_url_default_unchanged():
    output = _minimal_output()
    assert "unsplash" in output.olympic_image_url

def test_ape_index_accepts_custom_value():
    output = _minimal_output(ape_index=1.067, ape_index_label="Elite Reach")
    assert output.ape_index == 1.067
    assert output.ape_index_label == "Elite Reach"
