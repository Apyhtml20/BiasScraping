from urllib.parse import urljoin

import httpx
import trafilatura
from bs4 import BeautifulSoup

from app.models.article import Article, ArticleImage, ArticleParagraph


class ArticleScraper:
    def __init__(self) -> None:
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 "
                "(KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        }

    async def scrape(self, url: str) -> Article:
        async with httpx.AsyncClient(
            timeout=httpx.Timeout(20.0),
            follow_redirects=True,
            headers=self.headers,
        ) as client:
            response = await client.get(url)
            response.raise_for_status()

        html = response.text
        final_url = str(response.url)

        title = self._extract_title(html)
        paragraphs = self._extract_paragraphs(html)
        images = self._extract_images(html, final_url)

        if not paragraphs:
            raise ValueError(
                "Unable to extract article content from the provided URL."
            )

        return Article(
            url=final_url,
            title=title,
            paragraphs=paragraphs,
            images=images,
        )

    def _extract_title(self, html: str) -> str | None:
        metadata = trafilatura.extract_metadata(html)

        if metadata and metadata.title:
            return metadata.title.strip()

        soup = BeautifulSoup(html, "lxml")

        h1 = soup.find("h1")

        if h1:
            return h1.get_text(" ", strip=True)

        title = soup.find("title")

        if title:
            return title.get_text(" ", strip=True)

        return None

    def _extract_paragraphs(
        self,
        html: str,
    ) -> list[ArticleParagraph]:
        extracted = trafilatura.extract(
            html,
            include_comments=False,
            include_tables=False,
            include_links=False,
            favor_precision=True,
        )

        if not extracted:
            return []

        texts = [
            text.strip()
            for text in extracted.splitlines()
            if text.strip()
        ]

        return [
            ArticleParagraph(
                id=f"paragraph_{index}",
                text=text,
            )
            for index, text in enumerate(texts, start=1)
        ]

    def _extract_images(
        self,
        html: str,
        base_url: str,
    ) -> list[ArticleImage]:
        soup = BeautifulSoup(html, "lxml")

        images: list[ArticleImage] = []
        seen_urls: set[str] = set()

        for image in soup.find_all("img"):
            source = self._get_image_source(image)

            if not source:
                continue

            image_url = urljoin(base_url, source)

            if not self._is_valid_image_url(image_url):
                continue

            if image_url in seen_urls:
                continue

            seen_urls.add(image_url)

            alt = image.get("alt")

            images.append(
                ArticleImage(
                    id=f"image_{len(images) + 1}",
                    url=image_url,
                    alt=alt.strip() if alt else None,
                    position="article",
                )
            )

        return images

    def _get_image_source(self, image) -> str | None:
        source = (
            image.get("src")
            or image.get("data-src")
            or image.get("data-lazy-src")
            or image.get("data-original")
        )

        if source:
            return source.strip()

        srcset = image.get("srcset")

        if srcset:
            return srcset.split(",")[0].strip().split(" ")[0]

        return None

    def _is_valid_image_url(
        self,
        url: str,
    ) -> bool:
        invalid_extensions = (
            ".svg",
            ".gif",
        )

        return not url.lower().endswith(invalid_extensions)