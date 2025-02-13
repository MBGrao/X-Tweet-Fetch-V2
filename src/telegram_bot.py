import os
import logging
import requests
from requests.exceptions import RequestException
from dotenv import load_dotenv

# Load environment variables from the config/.env file
load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config/.env'))

logger = logging.getLogger(__name__)

class TelegramBot:
    def __init__(self):
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID")
        if not self.bot_token or not self.chat_id:
            raise ValueError("TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID is not set in the environment")
        self.api_url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"

    def send_message(self, message):
        payload = {
            "chat_id": self.chat_id,
            "text": message
        }
        try:
            response = requests.post(self.api_url, data=payload, timeout=10)
            response.raise_for_status()
            logger.info("Message sent to Telegram successfully")
            return response.json()
        except RequestException as e:
            logger.error(f"Error sending message to Telegram: {e}")
            raise
