# Architecture

## Overview

BiasScraping audits a news article for inclusivity: it scrapes the page, analyzes the text
for biased/exclusionary language, analyzes the images for representation of people, combines
both into a score, and asks an LLM to explain the findings in plain language.

```
┌──────────────┐  POST /api/audit   ┌────────────────────────────────────────────┐
│   Angular    │ ──────────────────▶│               FastAPI backend               │
│   frontend   │                    │                                              │
└──────────────┘                    │  AuditOrchestrator.audit(url)                │
                                     │   1. ArticleScraper.scrape(url)              │
                                     │   2. asyncio.gather(                         │
                                     │        NLPAnalyzer.analyze(article),         │
                                     │        VisionAnalyzer.analyze(article)       │
                                     │      )                                       │
                                     │   3. ReportManager.create_report(...)        │
                                     │   4. LLM call → agent_analysis               │
                                     └────────────────────────────────────────────┘
```

Steps 2's two branches run concurrently: the NLP branch runs in a worker thread
(`asyncio.to_thread`, since the classifier is a synchronous, CPU-bound Hugging Face pipeline),
while the vision branch does its own image downloads asynchronously (`httpx.AsyncClient`) and
runs YOLO/OpenCV per image.

## Request lifecycle

1. **Scraping** (`app/scraping_system`) — `ArticleScraper.scrape(url)` fetches the raw HTML
   (`httpx`, with a browser-like User-Agent) and hands it to `extract_article`, which uses
   `trafilatura` to isolate the main article body (dropping nav/ads/related-content chrome) and
   falls back to a BeautifulSoup heuristic when trafilatura can't parse a page. Returns an
   `Article` (title, paragraphs, images).

2. **NLP analysis** (`app/nlp`) — each paragraph is cleaned (`TextPreprocessor`) and classified
   by `BiasClassifier` (zero-shot NLI, see `ml_pipelines.md`). Paragraphs whose top label isn't
   `neutral_inclusive` *and* clears a minimum confidence are recorded as issues.

3. **Vision analysis** (`app/vision`) — each image is downloaded and resized
   (`ImagePreprocessor`), then run through `ClassicalCVAnalyzer` (brightness/contrast/sharpness/
   edge density via OpenCV) and `YOLODetector` (person detection). `VisionFusion` combines both
   into a per-image result (people count, prominence, quality score).

4. **Reporting** (`app/reports`) — `ReportManager` merges the two module outputs into one
   `inclusivity_score` (`InclusivityScorer`, weighted 60% NLP / 40% vision), a flat `issues` list,
   and prioritized `recommendations` (`RecommendationEngine`).

5. **LLM summary** (`app/orchestrator`) — the structured report (JSON) is sent to an LLM on the
   NVIDIA NIM API with a system prompt (`system_prompt.md`) that constrains it to only reason
   over the given evidence, never infer demographics from images, and use cautious language.
   The result is attached as `agent_analysis`.

## Why a fresh `AuditOrchestrator` per request

`audit_router.py` currently instantiates `AuditOrchestrator()` (and therefore the NLP/vision
models) on every request rather than once at startup. This is simple and stateless, but means
the classifier pipeline and YOLO model are reloaded per request — acceptable for occasional
manual audits, but worth turning into an app-lifetime singleton (e.g. via a lifespan handler)
if this needs to serve concurrent traffic.

## Deployment

Two containers (`docker-compose.yml`): the FastAPI backend, and an nginx container serving the
Angular production build and reverse-proxying `/api/*` to the backend over the Docker network.
See the root `README.md` for run instructions.
