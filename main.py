import time
from wallapop.wallapop import search_wallapop, getUserReviews
import google_utils.gsheets as gsheets
# from telegram_utils.telegram_utils import send_telegram, get_chat_id

REFRESH_TIME = 600

if __name__ == "__main__":

    # TELEGRAM_CHAT_ID = get_chat_id()
    creds = gsheets.googleLogin()

    while True:

        for params in gsheets.readSpreadsheet(creds):
            print(params)

            new_items = search_wallapop(params, REFRESH_TIME)
            print(new_items)
            
            if new_items:
                for item in new_items:
                    reviews = getUserReviews(item['user_id'])
                    message = (
                        f"<b>{item['title']}</b>\n"
                        f"<b>Precio:</b> {item['price']}€\n"
                        # f"<b>Última Modificación:</b> {item[3]}\n"
                        f"<b>Descripción:</b> {item['description']}\n"
                        f"<b>Ubicación:</b> {item['location']}\n"
                        f"<b>URL:</b> <a href='{item['item_url']}'>{item['item_url']}</a>\n\n"
                    )

                    print(message)

                    # send_telegram(message, TELEGRAM_CHAT_ID)
                print("Telegram message sent.")
        time.sleep(REFRESH_TIME)