import unittest

from app import app


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


if __name__ == '__main__':
    unittest.main()
