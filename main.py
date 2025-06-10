import time
import os
import logging
import sys
import colorlog
from datetime import datetime
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
                    products = analyze_products(new_items)
                    if products == -1:
                        for product in new_items:
                            print(f"Título: {product["title"]}")
                            print(f"Precio de Wallapop: {product["price"]} €")
                            print(f"Ubicación: {product["location"]}")
                            print(f"Fecha de modificación: {product['date']}")
                            print(f"Valoración del vendedor: {getUserReviews(product['user_id'])}")
                            print(f"Link del producto: {product["item_url"]}\n")
                    else:
                        for product in products:
                            print(f"Título: {product.title}")
                            print(f"Precio recomendado por la IA: {product.max_price} €")
                            print(f"Precio de Wallapop: {product.price} €")
                            print(f"Ubicación: {product.location}")
                            print(f"Fecha de modificación: {product.date.strftime('%Y-%m-%d %H:%M:%S')}")
                            print(f"Valoración del vendedor: {product.user_rating}")
                            print(f"Análisis: {product.analysis}")
                            print(f"Puntuación de compra: {product.score}")
                            print(f"Link del producto: {product.item_url}\n")
                    # message = (
                    #     "f<b>{product.title}</b>\n"
                    #     f"<b>Precio recomendado por la IA:</b> {product.max_price}€\n"
                    #     f"<b>Precio de Wallapop:</b> {product.price}€\n"
                    #     f"<b>Ubicación:</b> {product.location}\n"
                    #     f"<b>Fecha de modificación:</b> {product.date.strftime('%Y-%m-%d %H:%M:%S')}\n"
                    #     f"<b>Valoración del vendedor:</b> {product.user_rating}\n"
                    #     f"<b>Análisis:</b> {product.analysis}\n"
                    #     f"<b>Puntuación de compra:</b> {product.score}\n"
                    #     f"<b>Link del producto:</b> <a href='{product.item_url}'>{product.item_url}</a>\n"
                    # )

                    #     logger.info(f"New Item: {product.title}")
                    #     send_telegram(message, TELEGRAM_CHAT_ID)
                    logger.info(f"Telegram message sent. Sleeping {REFRESH_TIME} seconds until next check.")
                else:
                    logger.info(f"No new items found for {params['ITEM']}. Sleeping {REFRESH_TIME} seconds until next check.")
            time.sleep(REFRESH_TIME)
    except KeyboardInterrupt:
        logger.warning("KeyboardInterrupt detected. Exiting...")
if __name__ == "__main__":
    main()