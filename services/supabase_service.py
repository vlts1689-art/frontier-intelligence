import os
import json
from typing import Any, Dict, List

from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")


class SupabaseService:
    def __init__(self, url: str | None = None, key: str | None = None):
        self.url = url or SUPABASE_URL
        self.key = key or SUPABASE_KEY
        self.client: Client | None = None
        if self.url and self.key:
            self.client = create_client(self.url, self.key)

    def save_records(self, table: str, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not self.client:
            return []
        try:
            response = self.client.table(table).insert(records).execute()
            return response.data or []
        except Exception as exc:
            if "column" in str(exc).lower() or "does not exist" in str(exc).lower():
                raise RuntimeError("Supabaseのnewsテーブルに追加列が存在しない可能性があります。schemaを更新してください。") from exc
            raise

    def fetch_existing_urls(self) -> List[str]:
        if not self.client:
            return []
        try:
            response = self.client.table("news").select("url").execute()
            return [item.get("url") for item in (response.data or []) if item.get("url")]
        except Exception:
            return []

    def fetch_latest_news(self, limit: int = 10) -> List[Dict[str, Any]]:
        if not self.client:
            return []

        try:
            response = (
                self.client.table("news")
                .select("title, description, url, topic, source, published_at, created_at, summary_ja, related_companies, importance, why_important")
                .order("created_at", desc=True)
                .limit(limit)
                .execute()
            )
        except Exception as exc:
            if "column" in str(exc).lower() or "does not exist" in str(exc).lower():
                try:
                    response = (
                        self.client.table("news")
                        .select("title, description, url, topic, source, published_at, created_at")
                        .order("created_at", desc=True)
                        .limit(limit)
                        .execute()
                    )
                except Exception:
                    return []
            else:
                return []

        return [
            {
                "title": item.get("title", ""),
                "description": item.get("description", ""),
                "source": item.get("source", ""),
                "published_at": item.get("published_at", ""),
                "topic": item.get("topic", ""),
                "url": item.get("url", ""),
                "summary_ja": item.get("summary_ja", ""),
                "related_companies": item.get("related_companies") or [],
                "importance": item.get("importance"),
                "why_important": item.get("why_important", ""),
            }
            for item in (response.data or [])
        ]
