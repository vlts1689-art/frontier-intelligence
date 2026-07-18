import unittest
from unittest.mock import patch

from scripts.fetch_and_store_news import fetch_and_store_news
from services.news_analysis_service import NewsAnalysisService


class NewsAnalysisServiceTests(unittest.TestCase):
    def test_analyze_article_generates_japanese_summary_and_score(self):
        service = NewsAnalysisService()
        article = {
            "title": "AI data center expansion drives demand for liquid cooling systems",
            "description": "New facilities in Japan are increasing orders for cooling equipment and power infrastructure.",
            "url": "https://example.com/news/1",
        }

        result = service.analyze_article(article)

        self.assertIn("summary_ja", result)
        self.assertIn("topic", result)
        self.assertIn("related_companies", result)
        self.assertIn("importance", result)
        self.assertIn("why_important", result)
        self.assertTrue(result["summary_ja"])
        self.assertEqual(result["topic"], "AIデータセンター")
        self.assertTrue(isinstance(result["related_companies"], list))
        self.assertTrue(0 <= result["importance"] <= 100)
        self.assertTrue(result["why_important"])


class FetchAndStoreNewsTests(unittest.TestCase):
    @patch("scripts.fetch_and_store_news.SupabaseService")
    @patch("scripts.fetch_and_store_news.NewsService")
    def test_fetch_and_store_news_skips_duplicates_and_reports_counts(self, mock_news_service, mock_supabase_service):
        news_service = mock_news_service.return_value
        supabase_service = mock_supabase_service.return_value

        news_service.fetch_news.side_effect = [
            [
                {"title": "AI data center demand rises", "description": "A new facility is planned.", "url": "https://example.com/news/a", "published_at": "2026-07-17T00:00:00Z"},
                {"title": "Duplicate article", "description": "The same article again.", "url": "https://example.com/news/a", "published_at": "2026-07-17T00:00:00Z"},
            ],
            [
                {"title": "Optical fiber order update", "description": "Orders are rising in Japan.", "url": "https://example.com/news/b", "published_at": "2026-07-17T00:00:00Z"},
            ],
        ]
        supabase_service.fetch_existing_urls.return_value = {"https://example.com/news/a"}
        supabase_service.save_records.return_value = [{"url": "https://example.com/news/b"}]

        result = fetch_and_store_news(["AI data center", "optical fiber"], page_size=2)

        self.assertEqual(result["saved_count"], 1)
        self.assertEqual(result["duplicate_count"], 1)
        self.assertEqual(result["failed_count"], 0)
        self.assertEqual(result["saved_urls"], ["https://example.com/news/b"])


if __name__ == "__main__":
    unittest.main()
