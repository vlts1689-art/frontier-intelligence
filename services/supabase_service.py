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
