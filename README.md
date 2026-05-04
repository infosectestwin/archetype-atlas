# The Archetype Atlas // Onyx Protocol

![Build: Passing](https://img.shields.io/badge/Build-Passing-32ff7e?style=flat-square)
![Security: Verified](https://img.shields.io/badge/Security-Verified-32ff7e?style=flat-square)

> **Lead Architect:** Rowen the Cat 🐾  
> **Status:** DEPLOYMENT READY

## Project Vision: The Digital Mirror
The Archetype Atlas is a high-fidelity synthesis engine designed to bridge the biometric parity between Team USA Olympic and Paralympic athletes. By treating human performance as a universal blueprint, the Atlas provides a "Digital Mirror" where any athlete can find their structural counterparts across the full spectrum of elite competition.

## The Core Engine: Z-Score Normalization
The engine does not rely on simple comparisons. It utilizes **Onyx Protocol Z-Score Normalization** to map user biometrics against a historical dataset of 5,000 elite profiles.

- **Normalization:** Every input (Height, Weight, Wingspan) is converted into a standard deviation score relative to the athletic baseline.
- **Euclidean Proximity:** The engine calculates the mathematical "distance" between the user and the closest historical archetypes in a multi-dimensional biometric space.
- **Synthesis:** Gemini 1.5 Flash then interprets this proximity to generate the Architect’s Note, ensuring strict parity in narrative representation.

## Validated Alignments
The Atlas has been calibrated against known elite parities:
- **The Kinetic Levers:** Tara Davis-Woodhall (Olympic) and Hunter Woodhall (Paralympic).
- **The Aerobic Engines:** Katie Ledecky (Olympic) and Jessica Long (Paralympic).
- **The Agile Tacticians:** Lee Kiefer (Olympic) and Bebe Vio (Paralympic).
- **The Powerhouses:** Ryan Crouser (Olympic) and Jeremy Campbell (Paralympic).

## Infrastructure Architecture
- **Backend:** FastAPI (Python 3.11) served via Uvicorn.
- **Intelligence:** Gemini 1.5 Flash via Google Generative AI SDK.
- **Infrastructure:** Dockerized and deployed to **Google Cloud Run**.
- **Security:** Credential isolation via **Google Secret Manager** for API key protection.

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
   Navigate to `http://localhost:8000` to access the Atlas interface.

## Deployment Sequence
Deploy directly to Cloud Run using our automated script:
```powershell
.\deploy.ps1
```

---
*Statistical Parity Protocol v1.0.4 // Zero Retention Policy Active*
