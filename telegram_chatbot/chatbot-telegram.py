import requests
import logging
import colorlog
import time
from datetime import datetime
import os
import sys
# from dotenv import load_dotenv

# load_dotenv()
logger = logging.getLogger("wallapop")
# # Telegram Data
# TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
# # TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
# BASE_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
BASE_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"
PERPLEXITY_API_KEY= os.getenv("PERPLEXITY_API_KEY")

stream_formatter = colorlog.ColoredFormatter(
    fmt=("%(cyan)s%(asctime)s%(reset)s %(log_color)s%(levelname)-8s%(reset)s %(message)s"),
    datefmt="%Y-%m-%d %H:%M:%S",
    log_colors={
        "DEBUG": "purple",
        "INFO": "green",
        "WARNING": "yellow",
        "ERROR": "red",
        "CRITICAL": "red",
    },
)
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(stream_formatter)
logging.root.addHandler(stream_handler)

logger = logging.getLogger("ppxy")
logger.setLevel(logging.DEBUG)

def getUsername(TELEGRAM_CHAT_ID):
    try:
        from usermap import user_map
        return user_map.get(str(TELEGRAM_CHAT_ID), TELEGRAM_CHAT_ID)
    except ImportError:
        logger.warning("No usermap.py file found.")
        return TELEGRAM_CHAT_ID
    except KeyError:
        logger.warning("Chat ID not found in usermap.py.")
        return TELEGRAM_CHAT_ID

def send_message(message, TELEGRAM_CHAT_ID, MESSAGE_ID):
    url = BASE_URL + "/sendMessage"
    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "reply_to_message_id": MESSAGE_ID,
        "parse_mode": "Markdown"
    }
    a = requests.post(url, data=data)
    logger.info(f"Message sent to {getUsername(TELEGRAM_CHAT_ID)}")

def get_updates(last_update_id=None):
    url = BASE_URL + "/getUpdates"
    params = {"timeout": 25}
    if last_update_id:
        params["offset"] = last_update_id
    try:

        resp = requests.get(url, params=params)
        resp.raise_for_status()
        data = resp.json()
        if "result" in data:
            return data["result"]
        else:
            logger.error(f"Error de API Telegram: {data}")
            return []
    except requests.exceptions.RequestException as e:
        logger.error(f"Error al obtener actualizaciones: {e}")
        return []

def perplexity(bot_message, user_message, sender):
    url = "https://api.perplexity.ai/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
    }
    payload = {
        "model": "sonar",
        "messages": [
            {
            "role": "system",
            "content": f"Eres un bot de Telegram. Lo que respondes es un mensaje citado. Habla con el usuario (nombre: {sender}), salúdale y responde en el idioma que usa, o en catalán si no sabes. No añadas citas y usa markdown. Si hay URL en el mensaje citado, intenta consultar su contenido."
            },
            {
            "role": "user",
            "content": f"Mensaje citado: {bot_message}\nMensaje actual: {user_message}"
            }
        ]
    }

    response = requests.post(url, json=payload, headers=headers)
    response = response.json()
    content = response['choices'][0]['message']['content']

    return content




if __name__ == "__main__":
    last_update_id = None
    try:
        test_resp = requests.get(f"{BASE_URL}/getMe", timeout=10)
        if test_resp.status_code != 200:
            logger.critical(f"Token inválido: {test_resp.text}")
            sys.exit(1)
        logger.info("Token de Telegram válido")
    except Exception as e:
        logger.critical(f"No se puede conectar a Telegram: {e}")
        sys.exit(1)

    while True:
        updates = get_updates(last_update_id)
        for update in updates:
            last_update_id = update["update_id"] + 1
            message = update.get("message")
            
            if message and "reply_to_message" in message:
                
                try:
                    bot_message = message['reply_to_message']['text']
                except KeyError:
                    bot_message = message['reply_to_message']['caption']
                sender = message['from']['first_name']

                perplexity_completion = perplexity(bot_message = bot_message, sender = sender, user_message = message["text"])
                send_message(
                    TELEGRAM_CHAT_ID=message["chat"]["id"], 
                    MESSAGE_ID=message["message_id"],
                    message=perplexity_completion
                )
                break

        time.sleep(1)