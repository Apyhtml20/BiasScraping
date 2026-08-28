"""HTTP fetching and top-level entry point for the article scraping pipeline."""
import sys

import httpx

from scraping_system.article_extractor import Article, extract_article

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    )
}
TIMEOUT = 15.0


def fetch_html(url: str) -> str:
    response = httpx.get(
        url, headers=DEFAULT_HEADERS, timeout=TIMEOUT, follow_redirects=True
    )
    response.raise_for_status()
    return response.text


def scrape(url: str) -> Article:
    """Fetch a news article URL and return its structured content."""
    html = fetch_html(url)
    return extract_article(html, url)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python -m scraping_system.scraper <article_url>")
        sys.exit(1)

    article = scrape(sys.argv[1])
    sys.stdout.reconfigure(encoding="utf-8")
    print(article.model_dump_json(indent=2))
