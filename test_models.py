from models import AtlasInsight
from pydantic import ValidationError

def test_validator():
    print("Testing AtlasInsight validator...")
    
    # Test failure case
    try:
        AtlasInsight(insight_text="The athlete is fast.", matched_archetype="The Powerhouse")
        print("FAIL: Validation should have failed for missing conditional phrasing.")
    except ValidationError as e:
        print(f"SUCCESS: Caught expected validation error: {e.errors()[0]['msg']}")

    # Test success case
    try:
        AtlasInsight(insight_text="The athlete's wingspan could lead to higher reach.", matched_archetype="The Kinetic Lever")
        print("SUCCESS: Validation passed for conditional phrasing.")
    except ValidationError as e:
        print(f"FAIL: Validation should have passed. Error: {e}")

if __name__ == "__main__":
    test_validator()
