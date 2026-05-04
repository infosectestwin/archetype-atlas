import csv
import random

# Lead Architect Rowen's Archetype Blueprints
# Updated with exact archetype IDs (slugs) as requested
ARCHETYPES = {
    "powerhouse": {
        "display_name": "The Powerhouse",
        "height": (180, 210),
        "weight": (100, 145),
        "wingspan": (185, 225),
        "traits": ["High Force", "Explosive Power", "Large Mass"],
        "olympic_sport": "Athletics - Shotput",
        "paralympic_sport": "Para Athletics - F57 Field",
        "classification": "F57"
    },
    "aerobic_engine": {
        "display_name": "The Aerobic Engine",
        "height": (160, 185),
        "weight": (45, 65),
        "wingspan": (160, 190),
        "traits": ["High VO2 Max", "Endurance", "Lean Mass"],
        "olympic_sport": "Athletics - Marathon",
        "paralympic_sport": "Para Athletics - T54 Racing",
        "classification": "T54"
    },
    "kinetic_lever": {
        "display_name": "The Kinetic Lever",
        "height": (190, 220),
        "weight": (75, 100),
        "wingspan": (200, 240),
        "traits": ["Vertical Reach", "Long Levers", "High Center of Mass"],
        "olympic_sport": "Athletics - High Jump",
        "paralympic_sport": "Sitting Volleyball",
        "classification": "VS1"
    },
    "compact_dynamo": {
        "display_name": "The Compact Dynamo",
        "height": (145, 165),
        "weight": (40, 60),
        "wingspan": (140, 170),
        "traits": ["Low Center of Gravity", "High Strength-to-Weight", "Agility"],
        "olympic_sport": "Gymnastics",
        "paralympic_sport": "Para Powerlifting",
        "classification": "PO"
    },
    "aquatic_glider": {
        "display_name": "The Aquatic Glider",
        "height": (185, 205),
        "weight": (80, 105),
        "wingspan": (195, 220),
        "traits": ["Broad Shoulders", "Hydrodynamic Efficiency", "Large Hands/Feet"],
        "olympic_sport": "Swimming",
        "paralympic_sport": "Para Swimming - S9",
        "classification": "S9"
    },
    "agile_tactician": {
        "display_name": "The Agile Tactician",
        "height": (170, 195),
        "weight": (65, 85),
        "wingspan": (175, 205),
        "traits": ["Reaction Speed", "Precision", "Balanced Biometrics"],
        "olympic_sport": "Fencing",
        "paralympic_sport": "Wheelchair Fencing",
        "classification": "Cat A"
    }
}

def generate_data(num_records=5000):
    header = [
        "athlete_id", "name", "height_cm", "weight_kg", "wingspan_cm", 
        "sport", "year", "is_paralympic", "classification_code", "archetype"
    ]
    
    archetype_keys = list(ARCHETYPES.keys())
    records = []
    
    # Ensuring strict parity: 2500 Olympic, 2500 Paralympic
    for i in range(num_records):
        is_paralympic = i >= (num_records // 2)
        archetype_slug = random.choice(archetype_keys)
        blueprint = ARCHETYPES[archetype_slug]
        
        # Biometric generation based on blueprint
        height = round(random.uniform(*blueprint["height"]), 1)
        weight = round(random.uniform(*blueprint["weight"]), 1)
        wingspan = round(random.uniform(*blueprint["wingspan"]), 1)
        
        year = random.randint(1906, 2026)
        athlete_id = 1000 + i
        name = f"Athlete_{athlete_id}"
        
        if is_paralympic:
            sport = blueprint["paralympic_sport"]
            classification = blueprint["classification"]
        else:
            sport = blueprint["olympic_sport"]
            classification = ""
            
        records.append([
            athlete_id, name, height, weight, wingspan, 
            sport, year, is_paralympic, classification, archetype_slug
        ])
        
    random.shuffle(records)
    
    with open("historical_athletes.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(records)

if __name__ == "__main__":
    print("Rowen: 'Initializing data synthesis with exact archetype IDs...'")
    generate_data()
    print("Rowen: 'Synthesis complete. historical_athletes.csv generated.'")
