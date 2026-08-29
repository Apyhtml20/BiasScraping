from pydantic import BaseModel, Field


class ArticleParagraph(BaseModel):
    id: str
    text: str

class ArticleImage(BaseModel):
    id: str
    url: str
    alt: str | None = None
    position: str = "article"

class Article(BaseModel):
    url: str
    title: str | None = None
    paragraphs: list[ArticleParagraph] = Field(default_factory=list)
    images: list[ArticleImage] = Field(default_factory=list)