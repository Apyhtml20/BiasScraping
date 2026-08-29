"""Image extraction, scoped to main article content only."""
from urllib.parse import urljoin, urlparse

import trafilatura
from bs4 import BeautifulSoup

JUNK_URL_MARKERS = ("pixel.", "spacer.", "1x1", "tracking", "doubleclick", "blank.gif")
JUNK_CLASS_MARKERS = (
    "logo", "icon", "avatar", "sprite", "ad-", "advert", "banner",
    "related", "teaser", "recommend", "promo", "sponsored",
    "internallink", "more-stories", "read-more",
)
IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".avif")


def extract_images(html: str, url: str):
    """Article images with alt/caption, excluding logos, icons, ads and other page chrome."""
    from app.scraping_system.article_extractor import ArticleImage

    content_html = trafilatura.extract(
        html,
        url=url,
        output_format="html",
        favor_precision=True,
        include_images=True,
        include_comments=False,
        include_tables=False,
        include_links=False,
    )

    content_srcs = _collect_srcs(content_html) if content_html else None

    original_soup = BeautifulSoup(html, "lxml")

    if content_srcs is None:
        # trafilatura couldn't isolate the article body; fall back to a coarse heuristic
        # container so we still avoid nav/footer/header chrome.
        for tag in original_soup.find_all(["nav", "footer", "header", "aside"]):
            tag.decompose()
        container = original_soup.find("article") or original_soup.body or original_soup
        img_tags = container.find_all("img")
    else:
        all_imgs = original_soup.find_all("img")
        by_src = {
            urljoin(url, img.get("src")): img
            for img in all_imgs
            if img.get("src")
        }
        img_tags = [by_src[src] for src in content_srcs if src in by_src]

    seen: set[str] = set()
    images = []
    for img in img_tags:
        src = img.get("src")
        if not src:
            continue

        resolved_url = urljoin(url, src)
        if resolved_url in seen:
            continue
        if _is_junk(img, resolved_url, url):
            continue

        seen.add(resolved_url)
        images.append(
            ArticleImage(
                id=f"image_{len(images) + 1:02d}",
                url=resolved_url,
                alt=(img.get("alt") or "").strip() or None,
                caption=_find_caption(img),
                position="hero" if len(images) == 0 else "inline",
            )
        )

    return images


def _collect_srcs(content_html: str) -> list[str]:
    soup = BeautifulSoup(content_html, "lxml")
    return [tag.get("src") for tag in soup.find_all(attrs={"src": True})]


def _find_caption(img) -> str | None:
    figure = img.find_parent("figure")
    if figure:
        caption = figure.find("figcaption")
        if caption and caption.get_text(strip=True):
            return caption.get_text(" ", strip=True)

    parent = img.parent
    if parent:
        sibling_caption = parent.find_next_sibling(
            lambda tag: tag.name in ("figcaption", "span", "div", "p")
            and tag.get("class")
            and any("caption" in cls.lower() for cls in tag.get("class"))
        )
        if sibling_caption and sibling_caption.get_text(strip=True):
            return sibling_caption.get_text(" ", strip=True)

    return None


def _is_junk(img, resolved_url: str, article_url: str) -> bool:
    lower_url = resolved_url.lower()
    if urlparse(resolved_url).scheme not in ("http", "https", ""):
        return True
    if any(marker in lower_url for marker in JUNK_URL_MARKERS):
        return True

    try:
        width, height = int(img.get("width", 0)), int(img.get("height", 0))
        if 0 < width <= 2 or 0 < height <= 2:
            return True
    except (TypeError, ValueError):
        pass

    classes = " ".join(
        cls
        for tag in img.find_parents(limit=6)
        for cls in (tag.get("class") or [])
    ).lower()
    classes += " " + " ".join(img.get("class") or []).lower()
    if any(marker in classes for marker in JUNK_CLASS_MARKERS):
        return True

    link = img.find_parent("a")
    if link and link.get("href") and _links_to_other_page(link["href"], article_url):
        return True

    return False


def _links_to_other_page(href: str, article_url: str) -> bool:
    """True if an enclosing <a> points to a different page (a related-article card),
    rather than being a lightbox/self-link wrapper around the image itself."""
    resolved = urljoin(article_url, href)
    if resolved.lower().endswith(IMAGE_EXTENSIONS):
        return False

    href_path = urlparse(resolved).path.rstrip("/")
    article_path = urlparse(article_url).path.rstrip("/")
    return bool(href_path) and href_path != article_path
