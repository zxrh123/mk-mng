"""Fetch and enrich MikroTik knowledge base articles."""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Iterable

import httpx
from bs4 import BeautifulSoup

from app.core.config import settings
from app.core.logging import logger


class KnowledgeBaseCrawler:
    def __init__(self, storage_path: Path) -> None:
        self._storage_path = storage_path
        self._storage_path.mkdir(parents=True, exist_ok=True)
        self._sources = [
            "https://forum.mikrotik.com/",
            "https://wiki.mikrotik.com/wiki/Main_Page",
        ]

    async def refresh(self) -> None:
        async with httpx.AsyncClient(timeout=10.0) as client:
            tasks = [self._fetch_and_store(client, url) for url in self._sources]
            await asyncio.gather(*tasks)

    async def _fetch_and_store(self, client: httpx.AsyncClient, url: str) -> None:
        try:
            response = await client.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "lxml")
            text = soup.get_text(separator=" ", strip=True)[:5000]
            file_name = url.replace("https://", "").replace("/", "_") + ".txt"
            (self._storage_path / file_name).write_text(text, encoding="utf-8")
            logger.info("Knowledge base updated", source=url)
        except Exception as exc:  # pragma: no cover - remote IO
            logger.warning("Failed to refresh knowledge base from %s: %s", url, exc)

    def iter_documents(self) -> Iterable[str]:
        for file in self._storage_path.glob("*.txt"):
            yield file.read_text(encoding="utf-8")


knowledge_base_crawler = KnowledgeBaseCrawler(settings.knowledge_base_dir)

