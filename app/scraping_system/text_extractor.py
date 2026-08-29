"""Title and paragraph extraction, isolating main article content from boilerplate."""
from typing import Optional

import trafilatura
from bs4 import BeautifulSoup

MIN_PARAGRAPH_LENGTH = 40


def extract_title(html: str, url: str) -> Optional[str]:
    """Best-effort article title, preferring page metadata over DOM heuristics."""
    metadata = trafilatura.extract_metadata(html, default_url=url)
    if metadata and metadata.title:
        return metadata.title.strip()

    soup = BeautifulSoup(html, "lxml")
    h1 = soup.find("h1")
    if h1 and h1.get_text(strip=True):
        return h1.get_text(strip=True)

    if soup.title and soup.title.get_text(strip=True):
        return soup.title.get_text(strip=True)

    return None


def extract_paragraphs(html: str, url: str, title: Optional[str] = None):
    """Main article paragraphs, with navigation/ads/footers/related-content stripped out."""
    from app.scraping_system.article_extractor import ArticleParagraph

    text = trafilatura.extract(
        html,
        url=url,
        output_format="txt",
        favor_precision=True,
        include_comments=False,
        include_tables=False,
        include_images=False,
        include_links=False,
    )

    blocks = _split_blocks(text) if text else []

    if not blocks:
        blocks = _fallback_paragraphs(html)

    if title and blocks and blocks[0].strip().lower() == title.strip().lower():
        blocks = blocks[1:]

    return [
        ArticleParagraph(id=f"paragraph_{i:02d}", text=block)
        for i, block in enumerate(blocks, start=1)
    ]


def _split_blocks(text: str) -> list[str]:
    blocks = [line.strip() for line in text.split("\n") if line.strip()]
    return [block for block in blocks if len(block) >= MIN_PARAGRAPH_LENGTH]


def _fallback_paragraphs(html: str) -> list[str]:
    """Heuristic fallback for pages trafilatura fails to parse (e.g. very short pages)."""
    soup = BeautifulSoup(html, "lxml")

    for tag in soup.find_all(["nav", "footer", "header", "aside", "script", "style", "form"]):
        tag.decompose()

    container = soup.find("article") or soup.body or soup
    blocks = []
    for p in container.find_all("p"):
        text = p.get_text(" ", strip=True)
        if len(text) >= MIN_PARAGRAPH_LENGTH:
            blocks.append(text)
    return blocks
