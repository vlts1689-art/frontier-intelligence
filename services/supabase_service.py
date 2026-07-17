import os
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
        response = self.client.table(table).insert(records).execute()
        return response.data or []

    def fetch_latest_news(self, limit: int = 10) -> List[Dict[str, Any]]:
        if not self.client:
            return []

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

        return [
            {
                "title": item.get("title", ""),
                "description": item.get("description", ""),
                "source": item.get("source", ""),
                "published_at": item.get("published_at", ""),
                "topic": item.get("topic", ""),
                "url": item.get("url", ""),
            }
            for item in (response.data or [])
        ]
