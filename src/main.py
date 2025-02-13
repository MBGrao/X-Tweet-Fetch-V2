import os
import json
import time
import requests
import logging
from requests.exceptions import RequestException
from dotenv import load_dotenv

# Determine current directory (src) and project root (one directory up)
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, ".."))

# Build path to .env file in the config folder and load it
env_path = os.path.join(project_root, "config", ".env")
load_dotenv(dotenv_path=env_path)
print("Loaded .env from:", env_path)

# Setup logging configuration.
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Retrieve credentials and settings from .env.
TWITTER_BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
TARGET_USER = os.getenv("TARGET_USER")

if not TWITTER_BEARER_TOKEN:
    raise ValueError("TWITTER_BEARER_TOKEN is not set in the environment")
if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
    raise ValueError("TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID is not set in the environment")
if not TARGET_USER:
    raise ValueError("TARGET_USER is not set in the environment")

def create_headers(bearer_token):
    return {"Authorization": f"Bearer {bearer_token}"}

def poll_recent_tweets(headers, query, since_id=None):
    """
    Polls the Twitter API v2 recent search endpoint for tweets matching the query.
    Uses max_results=10 (the minimum allowed).
    """
    search_url = "https://api.twitter.com/2/tweets/search/recent"
    params = {
        "query": query,
        "max_results": "10"
    }
    if since_id:
        params["since_id"] = since_id
    response = requests.get(search_url, headers=headers, params=params, timeout=10)
    if response.status_code != 200:
        raise Exception(f"Cannot get recent tweets (HTTP {response.status_code}): {response.text}")
    return response.json()

def send_message_to_telegram(message):
    """
    Sends a message to your Telegram chat using the Bot API.
    """
    api_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    try:
        response = requests.post(api_url, data=payload, timeout=10)
        response.raise_for_status()
        logger.info("Message sent to Telegram successfully.")
        return response.json()
    except RequestException as e:
        logger.error(f"Error sending Telegram message: {e}")
        return None

def process_recent_tweets():
    """
    Polls the recent tweets endpoint for tweets from the target user.
    Returns True if at least one new tweet is processed; otherwise False.
    Implements handling for rate-limit errors.
    """
    global last_tweet_id
    query = f"from:{TARGET_USER}"
    try:
        data = poll_recent_tweets(headers, query, since_id=last_tweet_id)
        tweets = data.get("data", [])
        if tweets:
            # Twitter returns tweets in reverse chronological order.
            # Reverse to process oldest first.
            tweets = tweets[::-1]
            for tweet in tweets:
                tweet_id = tweet.get("id")
                tweet_text = tweet.get("text")
                message = f"New tweet from @{TARGET_USER}: {tweet_text}"
                send_message_to_telegram(message)
                logger.info(f"Processed tweet id {tweet_id}")
                last_tweet_id = tweet_id
            return True
        else:
            logger.info("No new tweets found.")
            return False
    except Exception as e:
        err_str = str(e)
        if "HTTP 429" in err_str:
            logger.error("Rate limit hit (HTTP 429). Sleeping for 30 seconds.")
            time.sleep(30)
            return False
        else:
            logger.error(f"Error polling tweets: {e}")
            return False

if __name__ == "__main__":
    headers = create_headers(TWITTER_BEARER_TOKEN)
    last_tweet_id = None  # Cache for the last processed tweet ID
    logger.info(f"Starting to poll tweets from @{TARGET_USER}...")

    # Adaptive polling configuration.
    base_interval = 3      # Base interval when tweets are found.
    additional_delay = 0   # Extra delay added if no tweets are found.
    max_interval = 60      # Maximum interval (in seconds).

    while True:
        found_new = process_recent_tweets()
        if found_new:
            # Reset delay if new tweet(s) found.
            additional_delay = 0
            sleep_interval = base_interval
        else:
            # Increase delay by 10 seconds, up to max_interval.
            additional_delay = min(additional_delay + 30, max_interval - base_interval)
            sleep_interval = base_interval + additional_delay
        logger.info(f"Sleeping for {sleep_interval} seconds before next poll.")
        time.sleep(sleep_interval)
