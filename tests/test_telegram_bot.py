import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import unittest
from unittest.mock import patch, Mock
from src import telegram_bot

class TestTelegramBot(unittest.TestCase):
    def setUp(self):
        os.environ["TELEGRAM_BOT_TOKEN"] = "TEST_TELEGRAM_BOT_TOKEN"
        os.environ["TELEGRAM_CHAT_ID"] = "123456789"
        self.bot = telegram_bot.TelegramBot()

    @patch('src.telegram_bot.requests.post')
    def test_send_message_success(self, mock_post):
        expected_response = {"ok": True, "result": {"message_id": 1}}
        mock_resp = Mock()
        mock_resp.raise_for_status.return_value = None
        mock_resp.json.return_value = expected_response
        mock_post.return_value = mock_resp

        result = self.bot.send_message("Hello Telegram")
        self.assertEqual(result, expected_response)
        mock_post.assert_called_once()

if __name__ == '__main__':
    unittest.main()
