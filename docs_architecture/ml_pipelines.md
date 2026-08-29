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
analyzed images, then combined with the NLP score 40/60 for the overall `inclusivity_score`.

**Known limitation:** the model only reports the *presence* of people, never demographic
attributes — this is enforced deliberately (see `system_prompt.md`'s rules for the LLM step)
since inferring gender/ethnicity/etc. from an image is out of scope and ethically risky for
this tool.

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
