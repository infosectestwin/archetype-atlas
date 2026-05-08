# Image Fallback, Ape Index & README Alignment Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Harden image resolution to use HALL_OF_FAME Unsplash URLs exclusively, add a labeled Ape Index stat to the result card, and align the `aerobic_engine` HALL_OF_FAME entry with the README source of truth (Elite Paralympic Swimmer).

**Architecture:** Targeted surgical fixes across three files — `models.py` (new fields + default fix), `engine.py` (data correction + wikimedia gate removal + ape_index computation), `index.html` (onerror handlers + placeholder divs + new stat block + JS population). A new module-level pure function `compute_ape_index` is extracted so it can be unit-tested without instantiating the engine.

**Tech Stack:** Python 3.11, Pydantic v2, FastAPI, Vertex AI (`vertexai` SDK), Tailwind CSS, Vanilla JS, pytest

---

## File Map

| File | Change |
|---|---|
| `models.py` | Add `ape_index: float`, `ape_index_label: str` to `EngineOutput`; fix `paralympic_image_url` default |
| `engine.py` | Add module-level `compute_ape_index()`; fix `HALL_OF_FAME["aerobic_engine"]`; remove wikimedia gate; call `compute_ape_index` in `generate_insight`; pass new fields to `EngineOutput` |
| `index.html` | Add `.img-placeholder` CSS + `@keyframes placeholder-pulse`; add sibling fallback divs to 3 image containers; add `onerror` to 3 `<img>` tags; add Ape Index stat block; populate in JS |
| `tests/test_models.py` | New file — unit tests for `EngineOutput` field defaults |
| `tests/test_engine_data.py` | New file — data integrity tests for `HALL_OF_FAME` and `compute_ape_index` |

---

### Task 1: Fix `models.py` — add ape_index fields and fix paralympic default

**Files:**
- Modify: `models.py:49-61`
- Create: `tests/test_models.py`

- [ ] **Step 1: Create `tests/` directory and write the failing tests**

Create `tests/__init__.py` (empty file), then create `tests/test_models.py`:

```python
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
```

- [ ] **Step 2: Run tests to confirm they fail**

```
cd D:\Python\TheArchetypeAtlas
.venv\Scripts\python -m pytest tests/test_models.py -v
```

Expected: `FAILED` — `EngineOutput` has no `ape_index` attribute; `paralympic_image_url` default is wrong.

- [ ] **Step 3: Update `models.py`**

Replace the current `EngineOutput` class (lines 49–61) with:

```python
class EngineOutput(BaseModel):
    archetype_match: ArchetypeMatch
    atlas_insight: AtlasInsight
    user_z_scores: BiometricZScores
    archetype_z_scores: BiometricZScores
    similarity_score: float
    matches: List[str] = Field(default_factory=list)
    olympic_match: str
    paralympic_match: str
    olympic_image_url: str = Field(default="https://images.unsplash.com/photo-1517836357463-d25dfeac3438?q=80&w=2070&auto=format&fit=crop")
    paralympic_image_url: str = Field(default="")
    architect_note: str
    system_node: str
    ape_index: float = 1.0
    ape_index_label: str = "Positive Index"
```

- [ ] **Step 4: Run tests to confirm they pass**

```
.venv\Scripts\python -m pytest tests/test_models.py -v
```

Expected: all 5 tests `PASSED`.

- [ ] **Step 5: Commit**

```
git add models.py tests/__init__.py tests/test_models.py
git commit -m "feat: add ape_index fields to EngineOutput; fix paralympic_image_url default"
```

---

### Task 2: Fix `HALL_OF_FAME["aerobic_engine"]` — swap in Elite Paralympic Swimmer

**Files:**
- Modify: `engine.py:29-34`
- Create: `tests/test_engine_data.py`

- [ ] **Step 1: Write failing data-integrity tests**

Create `tests/test_engine_data.py`:

```python
from engine import HALL_OF_FAME

def test_aerobic_engine_paralympic_is_elite_paralympic_swimmer():
    assert HALL_OF_FAME["aerobic_engine"]["paralympic"] == "Elite Paralympic Swimmer"

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
```

- [ ] **Step 2: Run tests to confirm they fail**

```
.venv\Scripts\python -m pytest tests/test_engine_data.py -v
```

Expected: `test_aerobic_engine_paralympic_is_elite_paralympic_swimmer` FAILS (`Elite Paralympic Racer != Elite Paralympic Swimmer`).

- [ ] **Step 3: Fix `HALL_OF_FAME["aerobic_engine"]` in `engine.py`**

Locate the `aerobic_engine` entry (around line 28) and replace the `paralympic` name only — the existing image URLs are already correct (two distinct Unsplash swimming shots):

```python
"aerobic_engine": {
    "olympic": "Elite Olympic Swimmer",
    "paralympic": "Elite Paralympic Swimmer",
    "olympic_image": "https://images.unsplash.com/photo-1530549387631-ce01ff996f9c?q=80&w=2070&auto=format&fit=crop",
    "paralympic_image": "https://images.unsplash.com/photo-1519315901367-f34ff9154487?q=80&w=2070&auto=format&fit=crop",
    "note": "Hydrodynamic efficiency and lean mass profile exemplify the 'Aerobic Engine' blueprint across disciplines."
},
```

> **URL note:** `photo-1519315901367-f34ff9154487` is already used in the codebase as a Paralympic aquatics shot and is known-good. Only the `paralympic` name changes.

- [ ] **Step 4: Run tests to confirm they pass**

```
.venv\Scripts\python -m pytest tests/test_engine_data.py -v
```

Expected: all 4 tests `PASSED`.

- [ ] **Step 5: Commit**

```
git add engine.py tests/test_engine_data.py
git commit -m "fix: swap Elite Paralympic Swimmer into aerobic_engine; fix duplicate image URLs in aquatic_glider"
```

---

### Task 3: Add `compute_ape_index` helper and unit tests

**Files:**
- Modify: `engine.py` (add module-level function before `HALL_OF_FAME`)
- Modify: `tests/test_engine_data.py` (add ape_index tests)

- [ ] **Step 1: Add ape_index tests to `tests/test_engine_data.py`**

Append to the existing file:

```python
from engine import HALL_OF_FAME, compute_ape_index

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
```

- [ ] **Step 2: Run tests to confirm they fail**

```
.venv\Scripts\python -m pytest tests/test_engine_data.py::test_ape_index_elite_reach -v
```

Expected: `FAILED` — `ImportError: cannot import name 'compute_ape_index' from 'engine'`.

- [ ] **Step 3: Add `compute_ape_index` to `engine.py`**

Add this function directly above the `HALL_OF_FAME` dict (before line 20):

```python
def compute_ape_index(wingspan_cm: float, height_cm: float) -> tuple[float, str]:
    index = round(wingspan_cm / height_cm, 3)
    if index > 1.03:
        label = "Elite Reach"
    elif index < 1.00:
        label = "Compact Profile"
    else:
        label = "Positive Index"
    return index, label
```

- [ ] **Step 4: Run all engine data tests**

```
.venv\Scripts\python -m pytest tests/test_engine_data.py -v
```

Expected: all 9 tests `PASSED`.

- [ ] **Step 5: Commit**

```
git add engine.py tests/test_engine_data.py
git commit -m "feat: add compute_ape_index pure function with boundary tests"
```

---

### Task 4: Wire `compute_ape_index` into `generate_insight` and remove wikimedia gate

**Files:**
- Modify: `engine.py:381-401` (ape_index call site), `engine.py:494-495` (wikimedia gate), `engine.py:524-544` (EngineOutput construction)

- [ ] **Step 1: Add ape_index computation in `generate_insight`**

In `engine.py`, inside `generate_insight`, locate the line:

```python
user_ratio = user_biometrics.wingspan_cm / user_biometrics.height_cm
```

Add immediately after it:

```python
ape_index, ape_index_label = compute_ape_index(user_biometrics.wingspan_cm, user_biometrics.height_cm)
```

- [ ] **Step 2: Remove the wikimedia gate**

Find lines 494–495:

```python
final_olympic_img = ai_data.image_url if (ai_data.image_url and "wikimedia" in ai_data.image_url.lower() and not user_biometrics.is_paralympic) else resolved_identity["olympic_image"]
final_paralympic_img = ai_data.image_url if (ai_data.image_url and "wikimedia" in ai_data.image_url.lower() and user_biometrics.is_paralympic) else resolved_identity["paralympic_image"]
```

Replace with:

```python
final_olympic_img = resolved_identity["olympic_image"]
final_paralympic_img = resolved_identity["paralympic_image"]
```

- [ ] **Step 3: Pass new fields to `EngineOutput`**

In the `EngineOutput(...)` construction (around line 524), add the two new fields:

```python
final_output = EngineOutput(
    archetype_match=ArchetypeMatch(
        archetype_name=ai_data.archetype_name,
        confidence_score=ai_data.confidence_score,
        shared_traits=ai_data.shared_traits
    ),
    atlas_insight=AtlasInsight(
        insight_text=ai_data.insight_text,
        matched_archetype=ai_data.archetype_name
    ),
    user_z_scores=user_z_obj,
    archetype_z_scores=archetype_z_obj,
    similarity_score=similarity_score,
    matches=ai_data.potential_matches or all_potential_archetypes,
    olympic_match=resolved_identity["olympic_match"],
    paralympic_match=resolved_identity["paralympic_match"],
    olympic_image_url=final_olympic_img,
    paralympic_image_url=final_paralympic_img,
    architect_note=architect_note,
    system_node=ai_data.system_node,
    ape_index=ape_index,
    ape_index_label=ape_index_label,
)
```

- [ ] **Step 4: Run full test suite**

```
.venv\Scripts\python -m pytest tests/ -v
```

Expected: all tests `PASSED`. The engine module must import cleanly — if there is an `ImportError` on `vertexai` or `google.genai`, that means the `.venv` is not activated. Run `.venv\Scripts\Activate.ps1` first.

- [ ] **Step 5: Commit**

```
git add engine.py
git commit -m "feat: wire ape_index into generate_insight; remove wikimedia image gate"
```

---

### Task 5: Frontend — image onerror handlers and frosted-glass placeholder

**Files:**
- Modify: `index.html` (CSS block + 3 image containers)

- [ ] **Step 1: Add CSS for `.img-placeholder` and the pulse keyframe**

In `index.html`, inside the `<style>` block, append before the closing `</style>` tag:

```css
@keyframes placeholder-pulse {
    0%   { opacity: 0.8; }
    50%  { opacity: 1.0; }
    100% { opacity: 0.8; }
}
.img-placeholder {
    background: rgba(255, 255, 255, 0.03);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.08);
    animation: placeholder-pulse 3s ease-in-out infinite;
    display: flex;
    align-items: center;
    justify-content: center;
}
.img-placeholder::after {
    content: '';
    width: 16px;
    height: 16px;
    border-radius: 50%;
    background: rgba(50, 255, 126, 0.15);
}
```

- [ ] **Step 2: Update the `archetypeImage` container (large 96×96 card thumbnail)**

Find the image wrapper for `archetypeImage`:

```html
<div class="relative w-24 h-24 rounded-2xl overflow-hidden border border-white/10 liquid-glass shrink-0">
    <img id="archetypeImage" src="" alt="Archetype Profile" class="w-full h-full object-cover opacity-80">
    <div class="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent"></div>
    <!-- Verified Badge -->
    <div class="absolute bottom-1 right-1 bg-[#32ff7e] rounded-full p-1 shadow-lg">
        <i data-lucide="check-check" class="w-3 h-3 text-black"></i>
    </div>
</div>
```

Replace with:

```html
<div class="relative w-24 h-24 rounded-2xl overflow-hidden border border-white/10 liquid-glass shrink-0">
    <img id="archetypeImage" src="" alt="Archetype Profile" class="w-full h-full object-cover opacity-80"
        onerror="this.onerror=null; this.style.display='none'; this.nextElementSibling.classList.remove('hidden');">
    <div id="archetypeImageFallback" class="img-placeholder hidden w-full h-full rounded-2xl"></div>
    <div class="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent pointer-events-none"></div>
    <div class="absolute bottom-1 right-1 bg-[#32ff7e] rounded-full p-1 shadow-lg">
        <i data-lucide="check-check" class="w-3 h-3 text-black"></i>
    </div>
</div>
```

- [ ] **Step 3: Update the `olympicImage` container (small 48×48 card)**

Find:

```html
<div class="w-12 h-12 rounded-xl overflow-hidden border border-white/10 shrink-0">
    <img id="olympicImage" src="" alt="Olympic Athlete" class="w-full h-full object-cover opacity-70">
</div>
```

Replace with:

```html
<div class="w-12 h-12 rounded-xl overflow-hidden border border-white/10 shrink-0">
    <img id="olympicImage" src="" alt="Olympic Athlete" class="w-full h-full object-cover opacity-70"
        onerror="this.onerror=null; this.style.display='none'; this.nextElementSibling.classList.remove('hidden');">
    <div id="olympicImageFallback" class="img-placeholder hidden w-full h-full rounded-xl"></div>
</div>
```

- [ ] **Step 4: Update the `paralympicImage` container (small 48×48 card)**

Find:

```html
<div class="w-12 h-12 rounded-xl overflow-hidden border border-white/10 shrink-0">
    <img id="paralympicImage" src="" alt="Paralympic Athlete" class="w-full h-full object-cover opacity-70">
</div>
```

Replace with:

```html
<div class="w-12 h-12 rounded-xl overflow-hidden border border-white/10 shrink-0">
    <img id="paralympicImage" src="" alt="Paralympic Athlete" class="w-full h-full object-cover opacity-70"
        onerror="this.onerror=null; this.style.display='none'; this.nextElementSibling.classList.remove('hidden');">
    <div id="paralympicImageFallback" class="img-placeholder hidden w-full h-full rounded-xl"></div>
</div>
```

- [ ] **Step 5: Reset fallback divs on each new analysis in JS**

In the `performAnalysis` JS function, in the "Input Clearing" block at the top (around line 525), add after the existing `olympicMatch`/`paralympicMatch` resets:

```js
['archetypeImageFallback', 'olympicImageFallback', 'paralympicImageFallback'].forEach(id => {
    const el = document.getElementById(id);
    if (el) el.classList.add('hidden');
});
['archetypeImage', 'olympicImage', 'paralympicImage'].forEach(id => {
    const el = document.getElementById(id);
    if (el) el.style.display = '';
});
```

- [ ] **Step 6: Commit**

```
git add index.html
git commit -m "feat: add frosted-glass onerror fallback to all archetype images"
```

---

### Task 6: Frontend — Ape Index stat block and JS population

**Files:**
- Modify: `index.html` (HTML stat block + JS)

- [ ] **Step 1: Add the Ape Index stat block below the Similarity Score**

Find the Similarity Score block:

```html
<!-- Similarity Score -->
<div class="text-center">
    <p class="text-[10px] uppercase tracking-[0.4em] text-neutral-600 mb-1">Similarity Index</p>
    <h4 id="similarityScore" class="text-4xl font-bold mono text-[#32ff7e] similarity-glow">98.4%</h4>
</div>
```

Replace with (adds the Ape Index block immediately below):

```html
<!-- Similarity Score -->
<div class="text-center">
    <p class="text-[10px] uppercase tracking-[0.4em] text-neutral-600 mb-1">Similarity Index</p>
    <h4 id="similarityScore" class="text-4xl font-bold mono text-[#32ff7e] similarity-glow">98.4%</h4>
</div>

<!-- Ape Index -->
<div class="text-center mt-4">
    <p class="text-[10px] uppercase tracking-[0.4em] text-neutral-600 mb-1">Ape Index</p>
    <div class="flex items-center justify-center gap-3">
        <span id="apeIndex" class="text-2xl font-bold mono text-[#32ff7e]">—</span>
        <span id="apeIndexLabel" class="text-[10px] mono uppercase tracking-widest text-neutral-400">—</span>
    </div>
</div>
```

- [ ] **Step 2: Populate Ape Index from API response in JS**

In `performAnalysis`, find the line:

```js
document.getElementById('similarityScore').innerText = result.similarity_score + "%";
```

Add immediately after it:

```js
document.getElementById('apeIndex').innerText = result.ape_index.toFixed(3);
document.getElementById('apeIndexLabel').innerText = result.ape_index_label;
```

- [ ] **Step 3: Reset Ape Index on new input (clean state)**

In the `inputs.forEach` `input` event listener (around line 457), find the block that resets `similarityScore`:

```js
document.getElementById('similarityScore').innerText = "0.0%";
```

Add immediately after it:

```js
document.getElementById('apeIndex').innerText = "—";
document.getElementById('apeIndexLabel').innerText = "—";
```

- [ ] **Step 4: Manual verification checklist**

Start the server: `.venv\Scripts\python -m uvicorn main:app --reload`

Open `http://localhost:8000` and verify:

- [ ] Enter `Height: 198, Weight: 85, Wingspan: 235` → Ape Index shows `1.187` with label `Elite Reach`
- [ ] Enter `Height: 142, Weight: 47, Wingspan: 142` → Ape Index shows `1.000` with label `Positive Index`
- [ ] Enter `Height: 180, Weight: 70, Wingspan: 178` → Ape Index shows `0.989` with label `Compact Profile`
- [ ] Open DevTools → Network tab → block `images.unsplash.com` → re-run analysis → all three image slots show the frosted-glass pulsing placeholder (not a broken image icon)
- [ ] Unblock `images.unsplash.com` → images load correctly, fallback divs are hidden

- [ ] **Step 5: Commit**

```
git add index.html
git commit -m "feat: add Ape Index stat to result card with Elite Reach / Compact Profile labeling"
```

---

## Post-Implementation

Run the full test suite one final time:

```
.venv\Scripts\python -m pytest tests/ -v
```

All tests should pass. The `system_node` tag in the UI should show `Onyx Prime` when Vertex AI answers — confirming the Vertex endpoint is the active synthesis path.
