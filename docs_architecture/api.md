# API Reference

Base URL (local dev): `http://localhost:8000`. All routes under `/api` are also reachable
through the Angular dev server on `http://localhost:4200` (proxied) or through the nginx
container on `http://localhost` in Docker.

## `GET /`

Liveness check.

```json
{ "message": "AI for Inclusion API is running" }
```

## `GET /health`

```json
{ "status": "healthy" }
```

## `POST /api/audit`

Runs a full audit on an article URL. This is a synchronous, single request/response call — it
does not stream progress. Expect it to take anywhere from a few seconds to over a minute,
depending on the article's length/image count and whether the ML models are already warm.

### Request

```json
{ "url": "https://example.com/news/some-article" }
```

| Field | Type | Notes |
| --- | --- | --- |
| `url` | string (URL) | Must be `http://` or `https://`. Validated by Pydantic's `HttpUrl`. |

### Response `200 OK` — `AuditReport`

```jsonc
{
  "audit_id": "uuid",
  "url": "https://example.com/news/some-article",
  "title": "Article title",
  "inclusivity_score": 88,          // 0-100, 60% NLP / 40% vision
  "summary": {
    "nlp_score": 100,
    "vision_score": 69,
    "total_issues": 3
  },
  "issues": [
    {
      "module": "nlp",                       // or "computer_vision"
      "paragraph_id": "paragraph_04",         // nlp issues only
      "text": "...",                          // nlp issues only
      "type": "gendered_language",            // or gender_stereotype / exclusionary_language / potential_bias / low_visual_representation
      "confidence": 0.78,                     // nlp issues only
      "severity": "high" | "medium" | "low",
      "message": "..."                        // computer_vision issues only
    }
  ],
  "recommendations": [
    { "module": "nlp", "type": "gendered_language", "message": "..." }
  ],
  "images": [
    {
      "image_id": "image_01",
      "image_url": "https://...",
      "alt": "...",
      "people_count": 1,
      "people_prominence": 0.0534,   // fraction of image area occupied by detected people
      "image_quality": 80.29,        // 0-100, from sharpness + contrast
      "brightness": 122.4,
      "contrast": 51.2,
      "sharpness": 594.32,
      "edge_density": 0.11,
      "contours": 240,
      "width": 480,
      "height": 270
    }
  ],
  "metadata": {
    "paragraphs_analyzed": 22,
    "images_found": 3,
    "images_analyzed": 3
  },
  "agent_analysis": "## Overall Assessment\n\n..."   // markdown, from the LLM
}
```

### Errors

Any exception raised anywhere in the pipeline (scraping failure, unreachable URL, model
error, missing `NVIDIA_API_KEY`, ...) is caught by the route and returned as:

```json
{ "detail": "<error message>" }
```

with HTTP status `500`. There is currently no distinction between client-caused failures
(e.g. a 404'd article URL) and server-side failures — both surface as 500 with a message.
`422` is returned automatically by FastAPI/Pydantic if `url` is missing or not a valid URL.
