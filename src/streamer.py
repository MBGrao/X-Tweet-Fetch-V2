import time
import logging
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from src.twitter_client import TwitterClient
from src.telegram_bot import TelegramBot

logger = logging.getLogger(__name__)

class Streamer:
    def __init__(self, usernames, poll_interval=3):  # Updated default poll_interval to 3 seconds
        """
        :param usernames: List of Twitter usernames to track.
        :param poll_interval: Polling interval in seconds.
        """
        self.lock = threading.Lock()
        self.usernames = usernames[:]  # make a copy
        self.poll_interval = poll_interval
        self.twitter_client = TwitterClient()
        self.telegram_bot = TelegramBot()
        # Dictionary to store last seen tweet ID per username.
        self.last_tweet_ids = {}
        # Dictionary to store backoff timestamp for accounts that hit rate limits.
        self.backoff_until = {}
        for username in self.usernames:
            self.last_tweet_ids[username] = None
            self.backoff_until[username] = 0  # no backoff initially

    def add_username(self, username):
        with self.lock:
            if username not in self.usernames:
                self.usernames.append(username)
                self.last_tweet_ids[username] = None
                self.backoff_until[username] = 0
                logger.info(f"Added new username: {username}")

    def check_username(self, username):
        now = time.time()
        # If we are in backoff mode for this user, skip checking.
        if now < self.backoff_until.get(username, 0):
            logger.info(f"Skipping {username} due to backoff until {self.backoff_until[username]}")
            return

        try:
            user_id = self.twitter_client.get_user_id(username)
            tweets_data = self.twitter_client.get_user_tweets(
                user_id, 
                since_id=self.last_tweet_ids.get(username)
            )
            tweets = tweets_data.get("data", [])
            if tweets:
                # Update last_tweet_ids so we do not resend the same tweet.
                with self.lock:
                    self.last_tweet_ids[username] = tweets[0].get("id")
                for tweet in tweets:
                    message = f"New tweet from {username}: {tweet.get('text')}"
                    self.telegram_bot.send_message(message)
                    logger.info(f"Forwarded tweet id {tweet.get('id')} from {username} to Telegram.")
        except Exception as e:
            error_str = str(e)
            # If error indicates a rate limit (429), set a backoff of, for example, 30 seconds.
            if "429" in error_str:
                backoff_time = 30  # seconds
                with self.lock:
                    self.backoff_until[username] = time.time() + backoff_time
                logger.error(f"Rate limit hit for {username}. Backing off for {backoff_time} seconds.")
            else:
                logger.error(f"Error processing tweets for {username}: {e}")

    def fetch_and_forward(self):
        # Use a thread pool to check all usernames concurrently.
        with ThreadPoolExecutor(max_workers=len(self.usernames)) as executor:
            futures = {executor.submit(self.check_username, username): username for username in self.usernames}
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    username = futures[future]
                    logger.error(f"Error processing {username}: {e}")

    def start_stream(self):
        logger.info("Starting tweet stream...")
        try:
            while True:
                self.fetch_and_forward()
                time.sleep(self.poll_interval)
        except KeyboardInterrupt:
            logger.info("Tweet stream stopped by user.")
        except Exception as e:
            logger.error(f"Stream encountered an error: {e}")
