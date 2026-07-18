import logging
import os
from datetime import datetime, timezone
from typing import Any, Dict, List

from services.news_analysis_service import NewsAnalysisService
from services.news_service import NewsService
from services.supabase_service import SupabaseService

logger = logging.getLogger(__name__)


DEFAULT_TOPICS = [
    "AI data center",
    "semiconductor",
    "power grid",
    "liquid cooling",
    "optical fiber",
    "cloud infrastructure",
]


def fetch_and_store_news(topics: List[str] | None = None, page_size: int = 5) -> Dict[str, Any]:
    topics = topics or DEFAULT_TOPICS
    news_service = NewsService()
    supabase_service = SupabaseService()
    analysis_service = NewsAnalysisService()

    saved_urls: List[str] = []
    duplicate_count = 0
    failed_count = 0
    fetched_count = 0
    seen_urls: set[str] = set()

    try:
        existing_urls = set(supabase_service.fetch_existing_urls() or [])
    except Exception:
        existing_urls = set()

    for topic in topics:
        try:
            articles = news_service.fetch_news(topic, page_size=page_size) or []
        except Exception as exc:
            failed_count += 1
            logger.exception("Failed to fetch news for topic %s", topic)
            continue

        fetched_count += len(articles)

        for article in articles:
            url = str(article.get("url") or "").strip()
            if not url:
                continue
            if url in seen_urls:
                continue
            if url in existing_urls:
                duplicate_count += 1
                seen_urls.add(url)
                continue

            seen_urls.add(url)

            analysis = analysis_service.analyze_article(article)
            record = {
                "title": article.get("title", "")[:200],
                "description": article.get("description", "")[:1000],
                "url": url,
                "topic": analysis["topic"],
                "source": "NewsAPI",
                "published_at": article.get("published_at", ""),
                "summary_ja": analysis["summary_ja"],
                "related_companies": analysis["related_companies"],
                "importance": analysis["importance"],
                "why_important": analysis["why_important"],
            }

            try:
                saved = supabase_service.save_records("news", [record])
            except Exception as exc:
                failed_count += 1
                logger.exception("Failed to save news article %s", url)
                continue

            if saved:
                existing_urls.add(url)
                saved_urls.append(url)

    completed_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    logger.info(
        "News refresh finished: fetched=%s saved=%s duplicates=%s failures=%s",
        fetched_count,
        len(saved_urls),
        duplicate_count,
        failed_count,
    )
    return {
        "saved_count": len(saved_urls),
        "duplicate_count": duplicate_count,
        "failed_count": failed_count,
        "fetched_count": fetched_count,
        "completed_at": completed_at,
        "saved_urls": saved_urls,
    }


if __name__ == "__main__":
    fetch_and_store_news()
