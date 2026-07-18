import unittest
from unittest.mock import patch

from app import app
from services.dashboard_service import get_dashboard_data


class FrontierRadarAppTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.client.testing = True

    def test_home_page_renders_dashboard(self):
        with patch('services.dashboard_service.SupabaseService') as mock_service:
            mock_service.return_value.fetch_latest_news.return_value = [
                {
                    'title': '最新ニュースの見出し',
                    'description': '実ニュースの説明',
                    'source': 'Reuters',
                    'published_at': '2026-07-17T00:00:00Z',
                    'topic': '液冷',
                    'url': 'https://example.com/news/1',
                }
            ]
            response = self.client.get('/')

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Frontier Radar', response.data)
        self.assertIn('今日見るべき変化'.encode('utf-8'), response.data)
        self.assertIn('最新ニュース'.encode('utf-8'), response.data)
        self.assertIn('最新ニュースの見出し', response.get_data(as_text=True))
        self.assertIn('液冷', response.get_data(as_text=True))
        self.assertIn('詳細を見る', response.get_data(as_text=True))
        self.assertIn('Xポストを生成', response.get_data(as_text=True))

    def test_dashboard_data_includes_news_and_stock_summary(self):
        with patch('services.dashboard_service.SupabaseService') as mock_service:
            mock_service.return_value.fetch_latest_news.return_value = [
                {
                    'title': '実ニュース',
                    'description': '実ニュース説明',
                    'source': 'Reuters',
                    'published_at': '2026-07-17T00:00:00Z',
                    'topic': '液冷',
                    'url': 'https://example.com/news/2',
                }
            ]
            dashboard = get_dashboard_data()

        self.assertIn('cards', dashboard)
        self.assertIn('latest_news', dashboard)
        self.assertTrue(len(dashboard['cards']) >= 1)
        self.assertIn('why_important', dashboard['cards'][0])
        self.assertIn('companies', dashboard['cards'][0])
        self.assertEqual(dashboard['latest_news'][0]['title'], '実ニュース')

    def test_dashboard_data_reports_fallback_message_when_no_news(self):
        with patch('services.dashboard_service.SupabaseService') as mock_service:
            mock_service.return_value.fetch_latest_news.return_value = []
            dashboard = get_dashboard_data()

        self.assertIn('latest_news_message', dashboard)
        self.assertIn('最新ニュース', dashboard['latest_news_message'])

    def test_refresh_news_endpoint_returns_success(self):
        with patch('app.refresh_news_data', return_value={'saved_count': 2, 'duplicate_count': 1, 'failed_count': 0, 'fetched_count': 4, 'completed_at': '2026-07-18 12:34:56', 'saved_urls': ['https://example.com/news/1']}):
            response = self.client.post('/refresh-news')

        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertTrue(payload['success'])
        self.assertEqual(payload['result']['saved_count'], 2)
        self.assertEqual(payload['result']['fetched_count'], 4)
        self.assertEqual(payload['result']['completed_at'], '2026-07-18 12:34:56')

    def test_home_route_uses_refresh_timestamp_query_param(self):
        with patch('app.get_dashboard_data', return_value={'overview': {'updated_at': 'old-time'}, 'cards': [], 'latest_news': [], 'latest_news_message': ''}):
            response = self.client.get('/?updated_at=2026-07-18%2012%3A34%3A56')

        self.assertEqual(response.status_code, 200)
        self.assertIn('2026-07-18 12:34:56', response.get_data(as_text=True))

    def test_refresh_news_endpoint_returns_error(self):
        with patch('app.refresh_news_data', side_effect=RuntimeError('更新失敗')):
            response = self.client.post('/refresh-news')

        self.assertEqual(response.status_code, 500)
        payload = response.get_json()
        self.assertFalse(payload['success'])
        self.assertIn('更新失敗', payload['error'])


if __name__ == '__main__':
    unittest.main()
