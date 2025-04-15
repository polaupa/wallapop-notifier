import requests
import time
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

# Wallapop Data
ITEM = os.getenv("ITEM")
REFRESH_TIME = int(os.getenv("REFRESH_TIME", 300))
MIN_PRICE = int(os.getenv("MIN_PRICE", 0))
MAX_PRICE = int(os.getenv("MAX_PRICE", 999999))

# Telegram Data
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def search_wallapop():
    url = "https://api.wallapop.com/api/v3/search?source=search_box&keywords=" + ITEM + "&longitude=2.1699187&latitude=41.387917&order_by=newest&min_sale_price=" + str(MIN_PRICE) + "&max_sale_price=" + str(MAX_PRICE)
    # url = "https://api.wallapop.com/api/v3/search?source=search_box&keywords=" + ITEM + "&longitude=-3.69196&latitude=40.41956"


    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "es,es-ES;q=0.9",
        "Connection": "keep-alive",
        "DeviceOS": "0",
        "Host": "api.wallapop.com",
        "MPID": "-2960643278018045342",
        "Origin": "https://es.wallapop.com",
        "Referer": "https://es.wallapop.com/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
        "X-DeviceID": "bbb",
        "X-AppVersion": "85020",
        "X-DeviceOS": "0",
        "sec-ch-ua": '"Google Chrome";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"macOS"'
    }


    response = requests.get(url, headers=headers)
    data = response.json()
    current_date = datetime.now()
    new_items = []

    for item in data["data"]["section"]["payload"]["items"]:
        title = item["title"]
        description = item["description"]
        price = item["price"]["amount"]
        timestamp = item["modified_at"]
        item_url = "https://es.wallapop.com/item/" + item["web_slug"]
        date = datetime.fromtimestamp(timestamp / 1000)
        difference = current_date - date

        # If item is newer than 2 minutes, print it
        if difference.seconds < REFRESH_TIME:
            new_items.append([title, description, price, date, item_url])
            # print("Item URL: " + item_url)
            # print("Title: " + title)
            # print("Price: " + str(price) + "€")
            # print("Date: " + str(date))
            # print("Description: " + description)
            # print("==========================")
    
    return new_items

def send_telegram(message):
    token = TELEGRAM_TOKEN
    chat_id = TELEGRAM_CHAT_ID
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML"
    }
    requests.post(url, data=data)

if __name__ == "__main__":

    while True:
        new_items = search_wallapop()
        print(new_items)

        if new_items:
            for item in new_items:
                message = (
                    f"<b>{item[0]}</b>\n"
                    f"<b>Precio:</b> {item[2]}€\n"
                    # f"<b>Última Modificación:</b> {item[3]}\n"
                    f"<b>Descripción:</b> {item[1]}\n"
                    f"<b>URL:</b> <a href='{item[4]}'>{item[4]}</a>\n\n"
                )
                send_telegram(message)
            print("Telegram message sent.")
        time.sleep(REFRESH_TIME)