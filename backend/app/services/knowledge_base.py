from __future__ import annotations

import asyncio
import contextlib
from datetime import datetime
from typing import Optional

import aiohttp
from bs4 import BeautifulSoup
from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.ai_providers import AIIntegrationGateway
from app.core.config import settings
from app.db.models import KnowledgeArticle


class KnowledgeBaseCrawler:
    def __init__(self, session_factory, ai_gateway: AIIntegrationGateway) -> None:
        self._session_factory = session_factory
        self._ai_gateway = ai_gateway
        self._interval = settings.knowledge_refresh_minutes * 60
        self._task: Optional[asyncio.Task] = None
        self._running = asyncio.Event()

    async def start(self) -> None:
        if not settings.enable_knowledge_crawler:
            logger.info("Knowledge crawler disabled via configuration")
            return
        self._running.set()
        if not self._task or self._task.done():
            self._task = asyncio.create_task(self._run_loop())

    async def stop(self) -> None:
        self._running.clear()
        if self._task:
            self._task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._task

    async def _run_loop(self) -> None:
        while self._running.is_set():
            try:
                await self.crawl_all()
            except Exception as exc:  # noqa: BLE001
                logger.exception("Knowledge crawler error: {}", exc)
            await asyncio.sleep(self._interval)

    async def crawl_all(self) -> None:
        for source_url in settings.knowledge_sources:
            await self._crawl_source(source_url)

    async def _crawl_source(self, source_url: str) -> None:
        logger.debug("Crawling knowledge source {}", source_url)
        async with aiohttp.ClientSession() as session:
            async with session.get(source_url, timeout=30) as response:
                response.raise_for_status()
                html = await response.text()

        soup = BeautifulSoup(html, "html.parser")
        title = soup.title.string.strip() if soup.title else source_url
        text_content = " ".join(p.get_text(strip=True) for p in soup.find_all("p"))

        summary_prompt = (
            "Summarize the following MikroTik knowledge article highlighting actionable insights, key metrics, "
            "and troubleshooting steps. Provide the response in JSON with fields title, key_points (array), "
            "and summary_ar (Arabic summary).\n\n"
            f"Content: {text_content[:4000]}"
        )
        synthesis = await self._ai_gateway.openai_provider.complete(summary_prompt)  # type: ignore[arg-type]

        async with self._session_factory() as db:  # type: AsyncSession
            article = await self._get_article(db, source_url)
            if not article:
                article = KnowledgeArticle(source_url=source_url, title=title, summary=synthesis, content=text_content)
                db.add(article)
            else:
                article.summary = synthesis
                article.content = text_content
                article.last_synced_at = datetime.utcnow()
            await db.commit()

    async def _get_article(self, session: AsyncSession, source_url: str) -> Optional[KnowledgeArticle]:
        result = await session.execute(select(KnowledgeArticle).where(KnowledgeArticle.source_url == source_url))
        return result.scalar_one_or_none()
