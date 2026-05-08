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
  This ratio is the mathematical "engine" that drives the specific athlete matches. It allows the Atlas to identify parity across different physical scales—matching the elongated reach of Michael Phelps (Aquatic Glider) or the precise, balanced levers of Lee Kiefer (Agile Tactician) to their Paralympic counterparts with clinical accuracy.

## Validation Matrix (Calibration Results v1.0.5)
The Atlas has been surgically calibrated against known elite parities:

| Profile Input | Height | Weight | Wingspan | Matched Archetype | Historical Parity Counterparts |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Case 1 (Fluid)** | 198cm | 90kg | 206cm | **The Aquatic Glider** | Michael Phelps [MP] // Mallory Weggemann |
| **Case 2 (Fencing)** | 183cm | 73kg | 193cm | **The Agile Tactician** | Lee Kiefer [LK] // Bebe Vio |
| **Case 3 (Track)** | 198cm | 85kg | 235cm | **The Kinetic Lever** | Tara Davis-Woodhall // Hunter Woodhall |
| **Case 4 (Swim)** | 168cm | 55kg | 170cm | **The Aerobic Engine** | Katie Ledecky // Jessica Long |
| **Case 5 (Force)** | 200cm | 130kg | 210cm | **The Powerhouse** | Ryan Crouser // Jeremy Campbell |
| **Case 6 (Torque)** | 142cm | 47kg | 142cm | **The Compact Dynamo** | Simone Biles // Bobby Body [Focus: Rotational Torque & CoM] |

*Similarity scores represent the biometric proximity to the archetype's statistical mean. Scores >80% indicate high-confidence functional alignment with the historical athlete's mechanical blueprint.*

## Stateless Security Architecture
The Atlas is built on a "Zero-Trust" foundation, utilizing **Stateless Security** to protect sensitive biometric data and credentials:

- **Google Cloud Run:** The application exists as a stateless containerized service. No user biometrics are persisted after the synthesis cycle completes.
- **Secret Manager:** API credentials (GOOGLE_API_KEY) are never stored in the codebase or environment files. They are injected at runtime via Google Secret Manager using the `:latest` version tag.
- **Ephemeral Infrastructure:** Each request is an isolated event, ensuring a clean slate and maximum privacy for the Onyx Protocol.

## Local Setup
Ensure you have Python 3.11+ installed.

1. **Clone & Initialize:**
   ```powershell
   git clone <repo-url>
   cd TheArchetypeAtlas
   ```

2. **Environment Configuration:**
   Create a `.env` file in the root:
   ```env
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
*Statistical Parity Protocol v1.0.5 // Onyx Protocol Active*
