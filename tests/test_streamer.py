import sys
import os
import unittest
from unittest.mock import patch, MagicMock

# Ensure the project root is in the sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src import streamer

class TestStreamer(unittest.TestCase):
    def setUp(self):
        self.usernames = ["testuser"]

    def test_fetch_and_forward(self):
        with patch('src.streamer.TwitterClient') as mock_twitter_client_cls, \
             patch('src.streamer.TelegramBot') as mock_telegram_bot_cls:

            # Create dummy instances for TwitterClient and TelegramBot.
            mock_twitter_client = MagicMock()
            mock_telegram_bot = MagicMock()
            mock_twitter_client_cls.return_value = mock_twitter_client
            mock_telegram_bot_cls.return_value = mock_telegram_bot

            # Prepare dummy responses for get_user_id and get_user_tweets.
            dummy_user_id = "12345"
            dummy_tweet = {"id": "111", "text": "Hello World"}
            mock_twitter_client.get_user_id.return_value = dummy_user_id
            mock_twitter_client.get_user_tweets.return_value = {"data": [dummy_tweet]}

            # Create a new instance of Streamer after patching.
            streamer_instance = streamer.Streamer(self.usernames, poll_interval=0)

            # Execute fetch_and_forward
            streamer_instance.fetch_and_forward()

            # Check that get_user_id and get_user_tweets were called with the correct parameters.
            mock_twitter_client.get_user_id.assert_called_with("testuser")
            mock_twitter_client.get_user_tweets.assert_called_with(dummy_user_id, since_id=None)

            # Check that TelegramBot's send_message was called with the correct message.
            expected_message = f"New tweet from testuser: {dummy_tweet.get('text')}"
            mock_telegram_bot.send_message.assert_called_with(expected_message)

    def test_fetch_and_forward_no_new_tweets(self):
        with patch('src.streamer.TwitterClient') as mock_twitter_client_cls, \
             patch('src.streamer.TelegramBot') as mock_telegram_bot_cls:

            # Create dummy instances for TwitterClient and TelegramBot.
            mock_twitter_client = MagicMock()
            mock_telegram_bot = MagicMock()
            mock_twitter_client_cls.return_value = mock_twitter_client
            mock_telegram_bot_cls.return_value = mock_telegram_bot

            # Prepare dummy responses: no new tweets.
            dummy_user_id = "12345"
            mock_twitter_client.get_user_id.return_value = dummy_user_id
            mock_twitter_client.get_user_tweets.return_value = {"data": []}

            # Create a new instance of Streamer after patching.
            streamer_instance = streamer.Streamer(self.usernames, poll_interval=0)

            # Execute fetch_and_forward
            streamer_instance.fetch_and_forward()

            # Verify that send_message was not called when no tweets are returned.
            mock_telegram_bot.send_message.assert_not_called()

if __name__ == '__main__':
    unittest.main()
