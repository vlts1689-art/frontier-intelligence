import unittest

from app import app
from services.dashboard_service import get_dashboard_data


class FrontierRadarAppTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.client.testing = True

    def test_home_page_renders_dashboard(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Frontier Radar', response.data)
        self.assertIn('今日の変化'.encode('utf-8'), response.data)
        self.assertIn('液冷'.encode('utf-8'), response.data)
        self.assertIn('詳細を見る'.encode('utf-8'), response.data)

    def test_dashboard_data_includes_news_and_stock_summary(self):
        dashboard = get_dashboard_data()
        self.assertIn('cards', dashboard)
        self.assertTrue(len(dashboard['cards']) >= 1)
        self.assertIn('why_important', dashboard['cards'][0])
        self.assertIn('companies', dashboard['cards'][0])


if __name__ == '__main__':
    unittest.main()
