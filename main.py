import time
import os
import logging
import sys
import colorlog
from dotenv import load_dotenv,set_key

from wallapop.wallapop import search_wallapop, getUserReviews
import google_utils.gsheets as gsheets
from telegram_utils.telegram_utils import send_telegram, get_chat_id
from wallapop.ai_analysis import analyze_products


REFRESH_TIME = 600
ENV_PATH = '.env'

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

logger = logging.getLogger("wallapop")
logger.setLevel(logging.INFO)



def main():

    load_dotenv(ENV_PATH)
    TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
    SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")

    if not TELEGRAM_CHAT_ID:
        TELEGRAM_CHAT_ID = get_chat_id()
        set_key(ENV_PATH, "TELEGRAM_CHAT_ID", TELEGRAM_CHAT_ID)
        logger.info("Telegram Chat ID saved in .env file.")
    else:
        logger.info(f"Using Telegram Chat ID: {TELEGRAM_CHAT_ID}")

    GCREDS = gsheets.googleLogin()

    try:
        while True:

            for params in gsheets.readSpreadsheet(GCREDS, SPREADSHEET_ID):
                new_items = search_wallapop(params, REFRESH_TIME)
                if new_items:
                    message = analyze_products(new_items)
                    # print(message)
                    # for item in new_items:
                    #     reviews = getUserReviews(item['user_id'])
                    #     message = (
                    #         f"<b>{item['title']}</b>\n"
                    #         f"<b>Precio:</b> {item['price']}€\n"
                    #         # f"<b>Última Modificación:</b> {item[3]}\n"
                    #         f"<b>Descripción:</b> {item['description']}\n"
                    #         f"<b>Ubicación:</b> {item['location']}\n"
                    #         f"<b>URL:</b> <a href='{item['item_url']}'>{item['item_url']}</a>\n"
                    #         f"<b>Valoración del vendedor:</b> {reviews} / 100\n"
                    #     )

                    #     logger.info(f"New Item: {item['title']}")
                    #     # send_telegram(message, TELEGRAM_CHAT_ID)
                    logger.info(f"Telegram message sent. Sleeping {REFRESH_TIME} seconds until next check.")
                else:
                    logger.info(f"No new items found for {params['ITEM']}. Sleeping {REFRESH_TIME} seconds until next check.")
            time.sleep(REFRESH_TIME)
    except KeyboardInterrupt:
        logger.warning("KeyboardInterrupt detected. Exiting...")
if __name__ == "__main__":
    main()