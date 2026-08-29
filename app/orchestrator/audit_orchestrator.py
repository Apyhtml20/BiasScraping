import asyncio
import json
import os

from openai import OpenAI

from app.scraping_system.scraper import ArticleScraper
from app.nlp.analyzer import NLPAnalyzer
from app.vision.analyzer import VisionAnalyzer
from app.reports.report_manager import ReportManager


class AuditOrchestrator:
    def __init__(self):
        self.client = OpenAI(
            base_url="https://integrate.api.nvidia.com/v1",
            api_key=os.getenv("NVIDIA_API_KEY")
        )

        self.scraper = ArticleScraper()
        self.nlp_analyzer = NLPAnalyzer()
        self.vision_analyzer = VisionAnalyzer()
        self.report_manager = ReportManager()

    async def audit(self, url: str) -> dict:
        article = await self.scraper.scrape(url)

        nlp_report, vision_report = await asyncio.gather(
            asyncio.to_thread(
                self.nlp_analyzer.analyze,
                article
            ),
            self.vision_analyzer.analyze(article))

        final_report = self.report_manager.create_report(
            article=article,
            nlp_report=nlp_report,
            vision_report=vision_report )

        agent_analysis = self._generate_agent_analysis(
            final_report )

        final_report["agent_analysis"] = agent_analysis

        return final_report

    def _generate_agent_analysis(
        self,
        report: dict) -> str:
        messages = [
            {
                "role": "system",
                "content": (
                    "You are an AI inclusion auditor. "
                    "Analyze structured NLP and computer "
                    "vision audit results. "
                    "Do not invent information. "
                    "Explain the most important findings and "
                    "provide practical inclusion recommendations."
                )
            },
            {
                "role": "user",
                "content": json.dumps(
                    report,
                    ensure_ascii=False,
                    indent=2
                )
            }
        ]
        response = self.client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=messages,
            temperature=0.3,
            max_tokens=1500
        )

        return response.choices[0].message.content