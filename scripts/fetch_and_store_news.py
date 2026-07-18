import os
from typing import Any, Dict, List

from services.news_analysis_service import NewsAnalysisService
from services.news_service import NewsService
from services.supabase_service import SupabaseService


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
    seen_urls: set[str] = set()

    try:
        existing_urls = set(supabase_service.fetch_existing_urls() or [])
    except Exception:
        existing_urls = set()

    for topic in topics:
        try:
            articles = news_service.fetch_news(topic, page_size=page_size) or []
        except Exception:
            failed_count += 1
            continue

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
            except Exception:
                failed_count += 1
                continue

            if saved:
                existing_urls.add(url)
                saved_urls.append(url)

    print(f"Saved: {len(saved_urls)}")
    print(f"Duplicates: {duplicate_count}")
    print(f"Failures: {failed_count}")
    return {
        "saved_count": len(saved_urls),
        "duplicate_count": duplicate_count,
        "failed_count": failed_count,
        "saved_urls": saved_urls,
    }


if __name__ == "__main__":
    fetch_and_store_news()
