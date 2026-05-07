from engine import HALL_OF_FAME

def test_aerobic_engine_paralympic_is_jessica_long():
    assert HALL_OF_FAME["aerobic_engine"]["paralympic"] == "Jessica Long"

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
