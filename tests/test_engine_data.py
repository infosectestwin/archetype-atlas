from engine import HALL_OF_FAME, compute_ape_index

def test_aerobic_engine_paralympic_title():
    assert HALL_OF_FAME["aerobic_engine"]["paralympic"] == "High-Capacity Para-Swimmer"

def test_aerobic_engine_images_are_unsplash():
    entry = HALL_OF_FAME["aerobic_engine"]
    assert "unsplash" in entry["olympic_image"]
    assert "unsplash" in entry["paralympic_image"]

def test_aerobic_engine_images_are_distinct():
    entry = HALL_OF_FAME["aerobic_engine"]
    assert entry["olympic_image"] != entry["paralympic_image"], \
        "aerobic_engine olympic and paralympic images must not be the same URL"

def test_all_entries_use_unsplash():
    for archetype, entry in HALL_OF_FAME.items():
        assert "unsplash" in entry["olympic_image"], \
            f"{archetype} olympic_image is not an Unsplash URL"
        assert "unsplash" in entry["paralympic_image"], \
            f"{archetype} paralympic_image is not an Unsplash URL"

def test_ape_index_elite_reach():
    idx, label = compute_ape_index(wingspan_cm=206.0, height_cm=198.0)
    assert idx == round(206.0 / 198.0, 3)
    assert label == "Elite Reach"

def test_ape_index_compact_profile():
    idx, label = compute_ape_index(wingspan_cm=140.0, height_cm=142.0)
    assert idx == round(140.0 / 142.0, 3)
    assert label == "Compact Profile"

def test_ape_index_positive_index():
    idx, label = compute_ape_index(wingspan_cm=183.0, height_cm=180.0)
    assert idx == round(183.0 / 180.0, 3)
    assert label == "Positive Index"

def test_ape_index_boundary_exactly_100():
    """1.0 exactly is NOT < 1.00, so it maps to Positive Index."""
    _, label = compute_ape_index(wingspan_cm=180.0, height_cm=180.0)
    assert label == "Positive Index"

def test_ape_index_boundary_exactly_103():
    """1.03 exactly is NOT > 1.03, so it maps to Positive Index."""
    wingspan = round(180.0 * 1.03, 4)
    _, label = compute_ape_index(wingspan_cm=wingspan, height_cm=180.0)
    assert label == "Positive Index"
