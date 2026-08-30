# ML Pipelines

## NLP: bias classification

`app/nlp/transformer_model.py` runs zero-shot classification
(`facebook/bart-large-mnli`, via `transformers.pipeline("zero-shot-classification")`) against
five candidate labels, `multi_label=False`:

- `neutral_inclusive`
- `gendered_language`
- `gender_stereotype`
- `exclusionary_language`
- `potential_bias`

Each paragraph gets a single top label + confidence. `NLPAnalyzer` (`app/nlp/analyzer.py`)
only records an issue when **both** are true:

- the top label isn't `neutral_inclusive`, and
- its confidence is at least `MIN_CONFIDENCE` (0.5).

**Why the threshold matters:** with 5 roughly-competing labels, a genuinely neutral sentence
still has to "win" one of them under `multi_label=False` — the random baseline is ~20%, and a
non-neutral label can easily edge out `neutral_inclusive` by a hair with a confidence in the
0.25–0.4 range that reflects noise, not a real signal. Without a floor, this flagged nearly
every paragraph of a normal, neutral article. The threshold trades some recall for precision;
tune `MIN_CONFIDENCE` up for stricter audits (fewer, more confident flags) or down for a more
sensitive pass.

Severity bands (`get_severity`): `>= 0.85` high, `>= 0.65` medium, else low.

`InclusivityScorer`/`NLPAnalyzer.calculate_score` currently penalizes purely on issue *count*
relative to total paragraphs, not confidence/severity — a single high-confidence issue and a
borderline one count the same. Worth revisiting if scoring needs to weight severity.

## Vision: person detection + image quality

Per image (`app/vision/analyzer.py`):

1. **Preprocessing** (`ImagePreprocessor`) — downloads the image, decodes it, resizes to at
   most 1280px wide.
2. **Classical CV** (`ClassicalCVAnalyzer`, OpenCV) — brightness (mean), contrast (stddev),
   sharpness (Laplacian variance), edge density and contour count (Canny).
3. **Person detection** (`YOLODetector`) — `ultralytics` YOLO, model `yolo11s.pt`, run at
   `conf=0.15`, `imgsz=960`. The small model + lowered confidence + larger inference size were
   chosen over the default nano/640/0.25 settings specifically to catch small or distant
   people (e.g. a crowd in an aerial shot) that the default config missed entirely in testing —
   at the cost of slightly more compute per image and a small risk of more false positives.
4. **Fusion** (`VisionFusion`) — combines both into `people_count`, `people_prominence`
   (detected-people bounding-box area ÷ image area, capped at 1.0), and `image_quality`
   (`sharpness` normalized against 500 weighted 60%, `contrast` normalized against 100 weighted
   40%, scaled to 0-100).

The vision score for the article (`_calculate_score`) is
`image_quality * 0.4 + (images_with_people / total_images * 100) * 0.6` — averaged across all
analyzed images. This feeds into the overall `inclusivity_score` alongside the NLP score and
the representation score below (see "Combining scores").

## Vision: perceived visual presentation (diversity & balance)

Per image, in addition to person detection, `VisionAnalyzer` runs a second, opt-in-by-design
pipeline over detected faces (`app/vision/analyzer.py::_analyze_faces`):

1. **Face detection** (`FaceDetector`, `app/vision/face_detector.py`) — OpenCV's
   `cv2.FaceDetectorYN` (YuNet), a small ONNX DNN model fetched on first use (like `ultralytics`'
   `.pt` files, it isn't committed to the repo — see `.gitignore`). Replaces the legacy
   `cv2.CascadeClassifier`, which is no longer exposed by the installed `opencv-python` (5.x)
   build.
2. **Presentation signal** (`PresentationSignalEstimator` + `PresentationModel`,
   `app/vision/presentation_signal.py` / `presentation_model.py`) — crops each detected face
   with a small margin and runs CLIP (`openai/clip-vit-base-patch32`, via
   `transformers.pipeline("zero-shot-image-classification")`) as a zero-shot classifier against
   three neutral prompts: feminine-presenting, masculine-presenting, androgynous/gender-neutral.
   Below `CONFIDENCE_THRESHOLD` (0.6) the face is bucketed `undetermined` instead of forcing a
   pick.
3. **Aggregation** (`RepresentationAggregator`, `app/vision/representation_aggregator.py`) —
   collects every face detected across the whole page into category counts/ratios, then computes:
   - `diversity_index` — normalized Shannon entropy over all 4 categories (including
     `undetermined`) — rewards multiple categories being present at all.
   - `balance_index` — normalized Shannon entropy over the 3 identified categories only —
     rewards an even split among faces that were confidently categorized.
   - `representation_score` = `((diversity_index + balance_index) / 2) * 100`.

   Below `MIN_FACES_FOR_SCORE` (3), these are all `None` (with a `note` explaining why) instead
   of returning a misleading 0 — entropy on a single face is trivially zero and isn't a
   meaningful diversity/balance signal.

**What this deliberately does *not* do:** identify any specific, real person's actual sex or
gender. Every "category" here is a coarse, low-confidence *visual presentation* signal
(hairstyle/clothing/features as read by a general-purpose image-text model), always reported in
aggregate at the page level, never attributed to a named or otherwise identifiable individual.
The `representation` block in the vision report always carries a `disclaimer` field stating
this, and `system_prompt.md` permits the LLM step to summarize the aggregated score but not to
translate it into a claim about anyone's real identity.

## Combining scores

`InclusivityScorer` (`app/reports/scoring.py`) combines up to three component scores — `nlp`
(weight 0.5), `vision` (0.25), `representation` (0.25) — via `build_breakdown`. When
`representation_score` is `None` (no faces, or fewer than `MIN_FACES_FOR_SCORE`), that component
is dropped and the remaining weights are renormalized rather than penalizing the page for having
no analyzable faces. `explain_breakdown` turns the weighted contributions into the
human-readable `score_explanation` list included in the final report, so every point of the
`inclusivity_score` is traceable to a specific component, its raw score, and its weight.

## LLM narrative step

`app/orchestrator/audit_orchestrator.py` serializes the structured report to JSON and sends it
to an LLM on the NVIDIA NIM API (`app/orchestrator/config.py`, model
`nvidia/nemotron-3-nano-30b-a3b`) with `system_prompt.md` as the system message. The prompt
enforces: no invented facts, no demographic inference from images, cautious hedging language,
and a fixed markdown structure (Overall Assessment / Key Findings / Linguistic Analysis /
Visual Analysis / Recommendations / Score Interpretation / Limitations).

This model was picked after benchmarking a few NVIDIA-hosted options on this exact prompt +
report shape: it completed in roughly half the time of `openai/gpt-oss-20b` while reliably
producing all required sections; a larger "lightning" reasoning variant was tried and rejected
for spending its whole token budget on hidden reasoning without reaching the final answer.
