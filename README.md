# The Archetype Atlas // Onyx Protocol

![Build: Passing](https://img.shields.io/badge/Build-Passing-32ff7e?style=flat-square)
![Security: Verified](https://img.shields.io/badge/Security-Verified-32ff7e?style=flat-square)
![Parity: Synchronized](https://img.shields.io/badge/Parity-Synchronized-32ff7e?style=flat-square)

> **Lead Architect:** Rowen the Cat 🐾  
> **Status:** DEPLOYMENT READY

## Project Vision: The Digital Mirror
The Archetype Atlas is a high-fidelity synthesis engine designed to bridge the biometric parity between Team USA Olympic and Paralympic athletes. By treating human performance as a universal blueprint, the Atlas provides a "Digital Mirror" where any athlete can find their structural counterparts across the full spectrum of elite competition.

## The Core Engine: Grounding & Z-Score Normalization
The engine does not rely on simple comparisons. It utilizes **Onyx Protocol Z-Score Normalization** to guide the AI synthesis.

- **The Grounding Mechanism:** Before **Gemini 2.5 Flash** (via Vertex AI) generates a single word, the Python core calculates the mathematical "distance" between the user and 5,000 elite profiles. This weighted Euclidean proximity serves as the immutable "Grounding" for the AI, preventing archetype drift and ensuring technical accuracy.
- **The Onyx Hierarchy:** A robust 3-tier failover system ensures 100% stability.
    - **Tier 1 (Onyx Prime):** Gemini 2.5 Flash via Google Vertex AI.
    - **Tier 2 (Relay Protocol):** Gemini 2.5 Pro via Google Gemini API.
    - **Tier 3 (Core Protocol):** Gemini 2.5 Flash via Google Gemini API.
- **Weighted Specificity:** For athletes above 185cm, the engine applies a 1.5x multiplier to the Weight parameter to distinguish between the lean profiles of Track & Field and the mass-heavy profiles of Swimming.
- **Ape Index (The Driving Metric):** The engine's primary differentiator is the **Ape Index**, defined as:
  $$\text{Ape Index} = \frac{\text{Wingspan}}{\text{Height}}$$
  This ratio is the mathematical "engine" that drives the specific archetype matches. It allows the Atlas to identify parity across different physical scales—matching the elongated reach of an Elite Hydrodynamic Swimmer (Aquatic Glider) or the precise, balanced levers of a High-Output Fencer (Agile Tactician) to their Paralympic counterparts with clinical accuracy.

## Validation Matrix (Calibration Results v1.0.6)
The Atlas has been surgically calibrated against known elite biometric parities:

| Profile Input | Height | Weight | Wingspan | Matched Archetype | Biometric Archetype Counterparts |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Case 1 (Fluid)** | 198cm | 90kg | 206cm | **The Aquatic Glider** | Elite Hydrodynamic Swimmer // High-Efficiency Para-Swimmer |
| **Case 2 (Fencing)** | 183cm | 73kg | 193cm | **The Agile Tactician** | High-Output Fencer // Precision Wheelchair Fencer |
| **Case 3 (Track)** | 198cm | 85kg | 235cm | **The Kinetic Lever** | Long-Lever Track Specialist // Mechanical Propulsion Specialist |
| **Case 4 (Swim)** | 168cm | 55kg | 170cm | **The Aerobic Engine** | Elite Endurance Swimmer // High-Capacity Para-Swimmer |
| **Case 5 (Force)** | 200cm | 130kg | 210cm | **The Powerhouse** | Heavy-Mass Shotput Specialist // High-Torque Discus Archetype |
| **Case 6 (Torque)** | 142cm | 47kg | 142cm | **The Compact Dynamo** | Elite Explosive Gymnast // Low-Gravity Powerlifter |

*Similarity scores represent the biometric proximity to the archetype's statistical mean. Scores >80% indicate high-confidence functional alignment with the mechanical blueprint.*

## Biometric Inference Engine (Science & Accuracy)
The Archetype Atlas utilizes a surgically calibrated **Biometric Inference Engine** to identify parity between athletes.

- **The Driving Metric (Ape Index):** The core differentiator is the **Ape Index**, defined as:
  $$\text{Ape Index} = \frac{\text{Wingspan}}{\text{Height}}$$
  This ratio serves as the mathematical foundation for determining mechanical reach and functional leverage across scales.
- **Euclidean Grounding:** The engine performs a **Z-score normalized Euclidean distance** calculation against a synthetic 120-year US athletic dataset. This ensures that every AI-generated insight is grounded in immutable biometric proximity rather than speculative inference.
- **Onyx Protocol v1.2:** By utilizing Z-score normalization, the Atlas accounts for standard deviations within each physical trait, allowing for precise matching between the high-torque profiles of a powerlifter and the explosive biometrics of a gymnast.

## Privacy-First Disclosure (Zero PII Policy)
To ensure absolute user privacy and zero PII (Personally Identifiable Information) exposure, the Atlas operates under a strictly anonymous protocol:

- **Reference IDs:** All historical references are mapped to anonymized **Reference IDs** (e.g., Athlete_4024 or USA-4024). 
- **Biometric Categorization:** Profiles are categorized purely by **Biometric Archetypes**. No real identity data (names, social handles, or personal histories) is stored, transmitted, or utilized within the synthesis core.
- **Stateless Execution:** Each request is an isolated, ephemeral event. User data is never persisted.

## Local Setup (v1.2 Stable)
Ensure you have Python 3.11+ installed.

1. **Clone & Initialize:**
   ```powershell
   git clone <repo-url>
   cd TheArchetypeAtlas
   ```

2. **Environment Configuration:**
   Create a `.env` file in the root:
   ```env
   PROJECT_ID=your-gcp-project-id
   LOCATION=us-central1
   GOOGLE_API_KEY=your_gemini_api_key_here
   ```

3. **Virtual Environment & Dependencies:**
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

4. **Data Generation:**
   Initialize the historical "Source of Truth":
   ```powershell
   python generate_atlas_data.py
   ```

5. **Execute Engine:**
   ```powershell
   python main.py
   ```

---
*Statistical Parity Protocol v1.2.0 // Production Ready*
