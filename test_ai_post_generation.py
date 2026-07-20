import os
import unittest
from unittest.mock import MagicMock, patch

from app import app
from services.post_generation_service import generate_ai_post


class OpenAIPostGenerationTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.client.testing = True

    def test_generate_ai_post_returns_error_without_api_key(self):
        with patch.dict(os.environ, {}, clear=True):
            result = generate_ai_post({
                "title": "半導体需要の見通しが緩やかに改善",
                "summary_ja": "市場参加者の関心が高まっている",
                "topic": "半導体",
                "related_companies": ["東京エレクトロン"],
                "url": "https://example.com/news/1",
            })

        self.assertFalse(result["success"])
        self.assertEqual(result["error"], "OpenAI APIキーが設定されていません。")

    def test_generate_ai_post_uses_mocked_openai_client(self):
        mock_response = MagicMock()
        mock_response.output_text = "半導体の需給に関心が高まっている。短期の方向感を見極めたい。"

        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key", "OPENAI_MODEL": "gpt-4.1-mini"}, clear=True):
            with patch("services.post_generation_service.OpenAI") as mock_openai:
                mock_openai.return_value.responses.create.return_value = mock_response
                result = generate_ai_post({
                    "title": "半導体需要の見通しが緩やかに改善",
                    "summary_ja": "市場参加者の関心が高まっている",
                    "topic": "半導体",
                    "related_companies": ["東京エレクトロン"],
                    "url": "https://example.com/news/1",
                })

        self.assertTrue(result["success"])
        self.assertEqual(result["post"], "半導体の需給に関心が高まっている。短期の方向感を見極めたい。")
        self.assertLessEqual(len(result["post"]), 140)

    def test_generate_ai_post_retries_when_response_is_too_long(self):
        long_response = MagicMock()
        long_response.output_text = "半導体需要の見通しが改善しそうだが、投資家の反応は慎重だ。関連企業の業績や供給網の動向を確認しながら、短期の値動きに一喜一憂しすぎない姿勢が大事だ。さらに、投資家が注目する供給制約や政策動向、需給の変化を見極める必要があるため、短期の反応に一喜一憂しすぎず、情報の整理を進める姿勢が重要だ。"
        short_response = MagicMock()
        short_response.output_text = "半導体需要の見通しは改善方向だが、短期の反応は慎重に見たい。"

        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key", "OPENAI_MODEL": "gpt-4.1-mini"}, clear=True):
            with patch("services.post_generation_service.OpenAI") as mock_openai:
                mock_openai.return_value.responses.create.side_effect = [long_response, short_response]
                result = generate_ai_post({
                    "title": "半導体需要の見通しが改善",
                    "summary_ja": "供給面の改善が期待される",
                    "topic": "半導体",
                    "related_companies": ["東京エレクトロン"],
                    "url": "https://example.com/news/2",
                })

        self.assertTrue(result["success"])
        self.assertLessEqual(len(result["post"]), 140)
        self.assertEqual(result["post"], "半導体需要の見通しは改善方向だが、短期の反応は慎重に見たい。")

    def test_generate_ai_post_route_returns_json(self):
        with patch("app.generate_ai_post", return_value={"success": True, "post": "短期の反応は慎重に見たい。", "length": 16}):
            response = self.client.post("/generate-ai-post", json={
                "title": "半導体需要の見通しが改善",
                "summary_ja": "供給面の改善が期待される",
                "topic": "半導体",
                "related_companies": ["東京エレクトロン"],
                "url": "https://example.com/news/3",
            })

        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertTrue(payload["success"])
        self.assertEqual(payload["post"], "短期の反応は慎重に見たい。")


if __name__ == "__main__":
    unittest.main()
