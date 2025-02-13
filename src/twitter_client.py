import os
import logging
import requests
from requests.exceptions import RequestException
from dotenv import load_dotenv

# Load environment variables from the config/.env file
load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config/.env'))

logger = logging.getLogger(__name__)

class TwitterClient:
    def __init__(self):
        self.bearer_token = os.getenv("TWITTER_BEARER_TOKEN")
        if not self.bearer_token:
            raise ValueError("TWITTER_BEARER_TOKEN is not set in the environment")
        self.api_url = "https://api.twitter.com/2"
        self.headers = {
            "Authorization": f"Bearer {self.bearer_token}"
        }
    
    def get_user_id(self, username):
        # Remove leading '@' if present
        username = username.lstrip('@')
        url = f"{self.api_url}/users/by/username/{username}"
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            user_id = data.get("data", {}).get("id")
            if not user_id:
                logger.error(f"User ID not found for username: {username}")
                raise ValueError("User ID not found in response")
            logger.info(f"Retrieved user id {user_id} for username {username}")
            return user_id
        except RequestException as e:
            logger.error(f"Error fetching user id for {username}: {e}")
            raise

    def get_user_tweets(self, user_id, since_id=None, max_results=5):
        url = f"{self.api_url}/users/{user_id}/tweets"
        params = {
            "max_results": max_results
        }
        if since_id:
            params["since_id"] = since_id
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            logger.info(f"Fetched tweets for user_id {user_id}")
            return data
        except RequestException as e:
            logger.error(f"Error fetching tweets for user_id {user_id}: {e}")
            raise
