import sys
import os
import unittest
from unittest.mock import patch, MagicMock

# Ensure the project root is in sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src import main

class TestMain(unittest.TestCase):
    @patch("src.main.TwitterClient")
    @patch("src.main.TelegramBot")
    @patch("builtins.input", side_effect=["testuser1, testuser2", "exit"])
    def test_process_accounts(self, mock_input, mock_telegram_cls, mock_twitter_cls):
        # Setup dummy TwitterClient instance
        dummy_twitter = MagicMock()
        dummy_twitter.get_user_id.side_effect = lambda username: f"id_{username}"
        dummy_twitter.get_user_tweets.return_value = {"data": [{"id": "1", "text": "Hello from test"}]}
        mock_twitter_cls.return_value = dummy_twitter

        # Setup dummy TelegramBot instance
        dummy_telegram = MagicMock()
        dummy_telegram.send_message.return_value = {"ok": True}
        mock_telegram_cls.return_value = dummy_telegram

        # Capture print output
        with patch("builtins.print") as mock_print:
            main.main()

            # Check that for each username, get_user_id and get_user_tweets were called
            dummy_twitter.get_user_id.assert_any_call("testuser1")
            dummy_twitter.get_user_id.assert_any_call("testuser2")
            self.assertEqual(dummy_twitter.get_user_tweets.call_count, 2)

            # Check that TelegramBot's send_message was called twice
            self.assertEqual(dummy_telegram.send_message.call_count, 2)

            # Check that the "Sent tweet" messages are printed
            calls = [call.args[0] for call in mock_print.call_args_list]
            self.assertTrue(any("Sent tweet from testuser1" in s for s in calls))
            self.assertTrue(any("Sent tweet from testuser2" in s for s in calls))

if __name__ == '__main__':
    unittest.main()
