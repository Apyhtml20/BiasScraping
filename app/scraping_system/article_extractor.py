from typing import Optional
from pydantic import BaseModel

from app.scraping_system.image_extractor import extract_images
from app.scraping_system.text_extractor import extract_paragraphs, extract_title

class ArticleImage(BaseModel):
 id: str
 url: str
 alt: Optional[str] = None
 caption: Optional[str] = None
 position: Optional[str] = None

class ArticleParagraph(BaseModel):
 id: str
 text: str

class Article(BaseModel):
 url: str
 title: Optional[str] = None
 paragraphs: list[ArticleParagraph]
 images: list[ArticleImage] = []

 @property
 def full_text(self) -> str:
  """Main article text, reassembled from paragraphs."""
  return "\n\n".join(p.text for p in self.paragraphs)


def extract_article(html: str, url: str) -> Article:
 """Extract a structured Article from raw page HTML, discarding nav/ads/footers/etc."""
 title = extract_title(html, url)
 paragraphs = extract_paragraphs(html, url, title)
 images = extract_images(html, url)
 return Article(url=url, title=title, paragraphs=paragraphs, images=images)
