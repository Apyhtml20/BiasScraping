import asyncio
import json
from pathlib import Path

from app.nlp.analyzer import NLPAnalyzer
from app.orchestrator.config import LLMConfig
from app.reports.report_manager import ReportManager
from app.scraping_system.scraper import ArticleScraper
from app.vision.analyzer import VisionAnalyzer


class AuditOrchestrator:
    def __init__(self):
        llm_config = LLMConfig()

        self.client = llm_config.create_client()
        self.model = llm_config.model

        self.scraper = ArticleScraper()
        self.nlp_analyzer = NLPAnalyzer()
        self.vision_analyzer = VisionAnalyzer()
        self.report_manager = ReportManager()

        self.system_prompt = self._load_system_prompt()

    async def audit(self, url: str) -> dict:
        article = await self.scraper.scrape(url)

        nlp_report, vision_report = await asyncio.gather(
            asyncio.to_thread(
                self.nlp_analyzer.analyze,
                article
            ),
            self.vision_analyzer.analyze(article)
        )

        structured_report = self.report_manager.create_report(
            article=article,
            nlp_report=nlp_report,
            vision_report=vision_report
        )

        agent_analysis = await asyncio.to_thread(
            self._generate_agent_analysis,
            structured_report
        )

        structured_report["agent_analysis"] = agent_analysis

        return structured_report

    def _load_system_prompt(self) -> str:
        prompt_path = Path(__file__).parent / "system_prompt.md"

        if not prompt_path.exists():
            raise FileNotFoundError(
                "system_prompt.md was not found."
            )

        return prompt_path.read_text(
            encoding="utf-8"
        )

    def _generate_agent_analysis(
        self,
        report: dict
    ) -> str:
        messages = [
            {
                "role": "system",
                "content": self.system_prompt
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
            model=self.model,
            messages=messages,
            temperature=0.3,
            max_tokens=1500
        )

        return response.choices[0].message.content