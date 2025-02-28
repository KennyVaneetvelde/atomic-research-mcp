import re
from typing import Optional
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from markdownify import markdownify
from pydantic import Field, HttpUrl
from readability import Document

from atomic_agents.agents.base_agent import BaseIOSchema
from atomic_agents.lib.base.base_tool import BaseTool, BaseToolConfig


class WebpageScraperToolInputSchema(BaseIOSchema):
    """Schema for webpage scraper input."""

    url: HttpUrl = Field(..., description="URL of the webpage to scrape.")


class WebpageMetadata(BaseIOSchema):
    """Schema for webpage metadata."""

    title: str = Field(..., description="The title of the webpage.")
    domain: str = Field(..., description="Domain name of the website.")
    description: Optional[str] = Field(
        None, description="Meta description of the webpage."
    )


class WebpageScraperToolOutputSchema(BaseIOSchema):
    """Schema for webpage scraper output."""

    content: str = Field(..., description="The scraped content in markdown format.")
    metadata: WebpageMetadata = Field(
        ..., description="Metadata about the scraped webpage."
    )


class WebpageScraperToolConfig(BaseToolConfig):
    """Configuration for the webpage scraper tool."""

    user_agent: str = Field(
        default="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        description="User agent string to use for requests.",
    )
    timeout: int = Field(
        default=30,
        description="Timeout in seconds for HTTP requests.",
    )


class WebpageScraperTool(BaseTool):
    """Tool for scraping webpage content."""

    input_schema = WebpageScraperToolInputSchema
    output_schema = WebpageScraperToolOutputSchema

    def __init__(self, config: WebpageScraperToolConfig = WebpageScraperToolConfig()):
        super().__init__(config)
        self.config = config

    def _fetch_webpage(self, url: str) -> str:
        """Fetches webpage content."""
        headers = {
            "User-Agent": self.config.user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        }
        response = requests.get(url, headers=headers, timeout=self.config.timeout)
        return response.text

    def _extract_metadata(
        self, soup: BeautifulSoup, doc: Document, url: str
    ) -> WebpageMetadata:
        """Extracts metadata from the webpage."""
        domain = urlparse(url).netloc
        description = None

        description_tag = soup.find("meta", attrs={"name": "description"})
        if description_tag:
            description = description_tag.get("content")

        return WebpageMetadata(
            title=doc.title(),
            domain=domain,
            description=description,
        )

    def _clean_markdown(self, markdown: str) -> str:
        """Cleans up markdown content."""
        markdown = re.sub(r"\n\s*\n\s*\n", "\n\n", markdown)
        markdown = "\n".join(line.rstrip() for line in markdown.splitlines())
        markdown = markdown.strip() + "\n"
        return markdown

    def _extract_main_content(self, soup: BeautifulSoup) -> str:
        """Extracts main content from webpage."""
        for element in soup.find_all(["script", "style", "nav", "header", "footer"]):
            element.decompose()

        content_candidates = [
            soup.find("main"),
            soup.find(id=re.compile(r"content|main", re.I)),
            soup.find(class_=re.compile(r"content|main", re.I)),
            soup.find("article"),
        ]

        main_content = next((c for c in content_candidates if c), None)
        if not main_content:
            main_content = soup.find("body")

        return str(main_content) if main_content else str(soup)

    def run(
        self, params: WebpageScraperToolInputSchema
    ) -> WebpageScraperToolOutputSchema:
        """Runs the webpage scraper tool."""
        html_content = self._fetch_webpage(str(params.url))
        soup = BeautifulSoup(html_content, "html.parser")
        doc = Document(html_content)

        main_content = self._extract_main_content(soup)
        markdown_content = markdownify(
            main_content,
            strip=["script", "style"],
            heading_style="ATX",
            bullets="-",
        )
        markdown_content = self._clean_markdown(markdown_content)
        metadata = self._extract_metadata(soup, doc, str(params.url))

        return WebpageScraperToolOutputSchema(
            content=markdown_content,
            metadata=metadata,
        )
