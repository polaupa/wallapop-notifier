import time
import os
import logging
import sys
import colorlog
import random
from datetime import datetime
from dotenv import load_dotenv,set_key
from googleapiclient.errors import HttpError


from wallapop.wallapop import search_wallapop, getUserReviews
import google_utils.gsheets as gsheets
from telegram_utils.telegram_utils import send_telegram, get_chat_id, html_parse
from wallapop.ai_analysis import analyze_products


REFRESH_TIME = 120
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
    SPREADSHEET_PUBLIC_URL_CSV = os.getenv("SPREADSHEET_PUBLIC_URL_CSV")

    if not TELEGRAM_CHAT_ID:
        TELEGRAM_CHAT_ID = get_chat_id()
        set_key(ENV_PATH, "TELEGRAM_CHAT_ID", TELEGRAM_CHAT_ID)
        logger.info("Telegram Chat ID saved in .env file.")
    else:
        logger.debug(f"Using Telegram Chat ID: {TELEGRAM_CHAT_ID}")    
    
    if not SPREADSHEET_ID:
        GCREDS = None
        logger.info("Public Google Sheets URL provided, no authentication needed.")
    else:
        GCREDS = gsheets.googleLogin()
        logger.info("Google Sheets credentials loaded successfully.")


    try:
        while True:
            try:
                if MOCK:
                    spreadsheet = mock_spreadsheet
                elif GCREDS:
                    spreadsheet = gsheets.readSpreadsheetWithAuth(GCREDS, SPREADSHEET_ID)
                else:
                    spreadsheet = gsheets.readSpreadsheetWithoutAuth(SPREADSHEET_PUBLIC_URL_CSV)
            except HttpError as e:
                logger.warning(f"Token Expired: {e}")
                GCREDS = gsheets.googleLogin()

            for params in spreadsheet:
                new_items = search_wallapop(params, REFRESH_TIME, MOCK)
                time.sleep(random.uniform(1, 3))
                if new_items:
                    products = analyze_products(new_items, params)
                    for product in products:
                        if product.score == None and product.user_reviews > 0:
                            html_product = html_parse(product)
                            send_telegram(html_product, TELEGRAM_CHAT_ID)
                        elif product.user_reviews <= params["MIN_REVIEWS"]:
                            logger.info(f"Item: {product.title} has {product.user_reviews} reviews. Skipping.")
                        elif product.score > MIN_SCORE and product.user_reviews >= params["MIN_REVIEWS"]:
                            html_product = html_parse(product)
                            send_telegram(html_product, TELEGRAM_CHAT_ID)
                            logger.info(f"Item: {product.title} is interesting (score: {product.score}, price {product.price}). Telegram message sent.")
                            logger.debug(product.analysis)
                        else:
                            logger.info(f"Item: {product.title} is not interesting enough (score: {product.score}, price {product.price}). Skipping.")
                            logger.debug(product.analysis)
                # else:
                #     logger.debug(f"No new items found for {params['ITEM']}.")
            # logger.debug(f"Sleeping {round(REFRESH_TIME/60,2)} minutes until next check.")
            time.sleep(REFRESH_TIME)
    except KeyboardInterrupt:
        logger.warning("KeyboardInterrupt detected. Exiting...")

if __name__ == "__main__":
    MOCK = False
    mock_spreadsheet = [{
        "ITEM": "piano digital", 
        "LONGITUDE": 2.1699187, 
        "LATITUDE": 41.38791, 
        "MIN_PRICE": 0, 
        "MAX_PRICE": 1000, 
        "MIN_REVIEWS": 90, 
        "DISTANCE": 10,
        # "MODEL": "magistral-medium-latest",
        # "MODEL": "sonar-pro",
        # "MODEL": "deepseek-chat",
        "MODEL": "gemini-2.5-pro",
        "PROMPT":"-"
    }]
    main()
