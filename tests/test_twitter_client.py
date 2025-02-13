import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import unittest
from unittest.mock import patch, Mock
from src import twitter_client

class TestTwitterClient(unittest.TestCase):
    def setUp(self):
        # Ensure a dummy bearer token is set for testing purposes
        os.environ["TWITTER_BEARER_TOKEN"] = "TEST_BEARER_TOKEN"
        self.client = twitter_client.TwitterClient()

    @patch('src.twitter_client.requests.get')
    def test_get_user_id_success(self, mock_get):
        expected_id = "12345"
        response_data = {
            "data": {
                "id": expected_id,
                "name": "Test User",
                "username": "testuser"
            }
        }
        mock_resp = Mock()
        mock_resp.raise_for_status.return_value = None
        mock_resp.json.return_value = response_data
        mock_get.return_value = mock_resp

        user_id = self.client.get_user_id("testuser")
        self.assertEqual(user_id, expected_id)
        mock_get.assert_called_once()

    @patch('src.twitter_client.requests.get')
    def test_get_user_tweets_success(self, mock_get):
        user_id = "12345"
        tweets_data = {
            "data": [
                {"id": "1", "text": "Hello World"}
            ]
        }
        mock_resp = Mock()
        mock_resp.raise_for_status.return_value = None
        mock_resp.json.return_value = tweets_data
        mock_get.return_value = mock_resp

        result = self.client.get_user_tweets(user_id)
        self.assertEqual(result, tweets_data)
        mock_get.assert_called_once()

if __name__ == '__main__':
    unittest.main()
