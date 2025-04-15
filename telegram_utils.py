import requests
import time
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

# Telegram Data
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
# TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
BASE_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

def send_telegram(message, TELEGRAM_CHAT_ID):
    url = BASE_URL + "/sendMessage"
    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    requests.post(url, data=data)

def get_updates(offset=None):
    params = {"timeout": 100}
    if offset:
        params["offset"] = offset
    resp = requests.get(f"{BASE_URL}/getUpdates", params=params)
    return resp.json()

def get_chat_id():
    print("Por favor, envía /start al bot en Telegram.")
    updates = get_updates()
    if updates.get("result"):
        last_update_id = updates["result"][-1]["update_id"] + 1
    else:
        last_update_id = None
    # last_update_id = None
    while True:
        updates = get_updates(last_update_id)
        for result in updates.get("result", []):
            last_update_id = result["update_id"] + 1
            message = result.get("message", {})
            text = message.get("text", "")
            if text == "/start":
                chat_id = message["chat"]["id"]
                print(f"¡Chat ID detectado! Tu chat_id es: {chat_id}")
                return chat_id
        time.sleep(1)