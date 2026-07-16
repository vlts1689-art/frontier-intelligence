import os
from typing import List, Dict, Any

import requests
from dotenv import load_dotenv

load_dotenv()

NEWS_API_KEY = os.getenv("NEWS_API_KEY", "")
NEWS_API_URL = "https://newsapi.org/v2/everything"


class NewsService:
    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or NEWS_API_KEY

    def fetch_news(self, query: str, page_size: int = 5) -> List[Dict[str, Any]]:
        if not self.api_key:
            return []

        params = {
            "q": query,
            "language": "en",
            "sortBy": "publishedAt",
            "pageSize": page_size,
            "apiKey": self.api_key,
        }
        response = requests.get(NEWS_API_URL, params=params, timeout=10)
        response.raise_for_status()
        payload = response.json()
        articles = payload.get("articles", [])
        return [
            {
                "title": article.get("title", "")[:120],
                "description": article.get("description", "")[:220],
                "url": article.get("url", ""),
                "published_at": article.get("publishedAt", ""),
            }
            for article in articles
        ]

    def collect_topic_news(self, topics: List[str]) -> Dict[str, List[Dict[str, Any]]]:
        result: Dict[str, List[Dict[str, Any]]] = {}
        for topic in topics:
            result[topic] = self.fetch_news(topic)
        return result
