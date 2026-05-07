# Design: Image Fallback, Ape Index, and README Alignment
**Date:** 2026-05-07  
**Approach:** Targeted surgical fixes (Approach A)  
**Files touched:** `engine.py`, `models.py`, `index.html`

---

## 1. Image Fallback

### Problem
`engine.py:494–495` gates on `"wikimedia" in ai_data.image_url` before using the AI's URL. Vertex AI / Gemini almost never returns a valid Wikimedia link, so the condition is effectively dead code — but it leaves a footgun where a hallucinated URL could slip through. `models.py:59` also has a copy-paste bug where `paralympic_image_url` defaults to the same Olympic Unsplash URL.

### Solution

**Backend (`engine.py`):**
- Remove the `wikimedia` gate entirely. Replace both `final_olympic_img` / `final_paralympic_img` assignments with direct reads from `resolved_identity`:
  ```python
  final_olympic_img = resolved_identity["olympic_image"]
  final_paralympic_img = resolved_identity["paralympic_image"]
  ```
- `ai_data.image_url` is still returned by the AI for logging/observability but never routed to the output.

**Model (`models.py`):**
- Fix `EngineOutput.paralympic_image_url` default to `""` (empty string) instead of duplicating the Olympic URL.

**Frontend (`index.html`):**
- Add `onerror` to all three `<img>` tags (`archetypeImage`, `olympicImage`, `paralympicImage`).
- Handler nulls itself then hides the broken img and reveals a pre-placed sibling fallback div (no external file dependency):
  ```js
  onerror="this.onerror=null; this.style.display='none'; this.nextElementSibling.classList.remove('hidden');"
  ```
- Each image wrapper gets a sibling `<div class="img-placeholder hidden liquid-glass ...">` that is invisible by default.
- Add CSS class `.img-placeholder` with a slow opacity pulse (`animation: placeholder-pulse 3s ease-in-out infinite`) cycling 0.8 → 1.0 opacity — subtle, non-distracting, maintains Liquid Glass aesthetic.

---

## 2. Ape Index

### Formula
```
Ape Index = Wingspan (cm) / Height (cm)
```

### Contextual Labels
| Value | Label |
|---|---|
| > 1.03 | Elite Reach |
| 1.00 – 1.03 | Positive Index |
| < 1.00 | Compact Profile |

### Backend (`engine.py`)
Compute immediately after the existing `user_ratio` line in `generate_insight`:
```python
ape_index = round(user_biometrics.wingspan_cm / user_biometrics.height_cm, 3)
ape_index_label = (
    "Elite Reach" if ape_index > 1.03
    else "Compact Profile" if ape_index < 1.00
    else "Positive Index"
)
```
Pass both into `EngineOutput`.

### Model (`models.py`)
Add to `EngineOutput`:
```python
ape_index: float = 1.0
ape_index_label: str = "Positive Index"
```

### Frontend (`index.html`)
Place a new stat block directly below the Similarity Score block:
```
APE INDEX            (text-[10px] uppercase tracking-[0.4em] text-neutral-600)
1.06  ELITE REACH    (mono text, cyber-lime value, neutral-400 label)
```
Font: `JetBrains Mono`. Value font-size slightly smaller than similarity score. Color: `#32ff7e` for the numeric value, `text-neutral-400` for the label string.

---

## 3. README / Code Alignment

### Problem
`HALL_OF_FAME["aerobic_engine"]` has `Tatyana McFadden` as the Paralympic counterpart to Katie Ledecky. The README validation matrix (the source of truth) specifies **Jessica Long** — a direct swimming-to-swimming parity match.

### Solution
**`engine.py` `HALL_OF_FAME["aerobic_engine"]`:**
- `paralympic` → `"Jessica Long"`
- `paralympic_image` → high-quality Paralympic swimming Unsplash URL (distinct from the Olympic swimming URL to avoid visual duplication). URL must be verified live during implementation; if the preferred photo is unavailable, use the nearest available Paralympic aquatics shot from Unsplash.

---

## Constraints & Edge Cases

- `onerror` must null itself (`this.onerror=null`) before reassigning `src` — prevents infinite redirect if the placeholder itself is missing.
- Ape Index of exactly `1.00` maps to "Positive Index" (not "Compact Profile") — boundary is `< 1.00` strictly.
- `ai_data.image_url` field stays in `AISynthesis` schema for observability — it is not removed, just never routed to output.
- `assets/archetype_placeholder.png` must exist before deployment; the spec assumes it will be created as part of implementation.
