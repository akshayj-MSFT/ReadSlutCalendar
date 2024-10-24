import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Replace these values with your own
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
TELEGRAM_TOPIC_ID = os.getenv('TELEGRAM_TOPIC_ID')

# Send a simple message to a Telegram chat


text = 'Hello, this is a test message!'

url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'
payload = {
    'chat_id': TELEGRAM_CHAT_ID,
    'message_thread_id': TELEGRAM_TOPIC_ID,
    'text': text
}

response = requests.post(url, json=payload)
print(response.json())
