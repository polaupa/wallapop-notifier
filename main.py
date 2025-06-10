import time
import os
import logging
import sys
import colorlog
from datetime import datetime
from dotenv import load_dotenv,set_key

from wallapop.wallapop import search_wallapop, getUserReviews
import google_utils.gsheets as gsheets
from telegram_utils.telegram_utils import send_telegram, get_chat_id, html_parse
from wallapop.ai_analysis import analyze_products


REFRESH_TIME = 600
ENV_PATH = '.env'
MIN_SCORE = 75

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
logger.setLevel(logging.DEBUG)



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
                    products = analyze_products(new_items)
                    for product in products:
                        if product.score == None and product.user_reviews > 0:
                            html_product = html_parse(product)
                            send_telegram(html_product, TELEGRAM_CHAT_ID)
                        elif product.user_reviews == 0:
                            logger.info(f"Item: {product.title} has no user reviews. Skipping.")
                        elif product.score > MIN_SCORE and product.user_reviews > 0:
                            html_product = html_parse(product)
                            send_telegram(html_product, TELEGRAM_CHAT_ID)
                            logger.info(f"Item: {product.title} is interesting (score: {product.score}). Telegram message sent.")
                        else:
                            logger.debug(f"Item: {product.title} is not interesting enough (score: {product.score}). Skipping.")
                            logger.debug(product.analysis)
                else:
                    logger.info(f"No new items found for {params['ITEM']}.")
            logger.info(f"Sleeping {round(REFRESH_TIME/60,2)} minutes until next check.")
            time.sleep(REFRESH_TIME)
    except KeyboardInterrupt:
        logger.warning("KeyboardInterrupt detected. Exiting...")
if __name__ == "__main__":
    main()