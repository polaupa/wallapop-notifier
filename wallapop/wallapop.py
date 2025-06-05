import requests
from datetime import datetime
from dotenv import load_dotenv
from urllib.parse import urlencode

load_dotenv()



# Wallapop Data
# ITEM = os.getenv("ITEM")
# MIN_PRICE = int(os.getenv("MIN_PRICE", 0))
# MAX_PRICE = int(os.getenv("MAX_PRICE", 1000))
# LONGITUDE = os.getenv("LONGITUDE",2.1699187) # Barcelona by default
# LATITUDE = os.getenv("LATITUDE",41.387917)
# DISTANCE = int(os.getenv("DISTANCE", 30))

def search_wallapop(params, REFRESH_TIME=120):
    # url = "https://api.wallapop.com/api/v3/search?source=search_box&keywords=" + params['ITEM'] + "&longitude=" + str(params['LONGITUDE']) + "&latitude=" + str(params['LATITUDE']) + "&order_by=newest&min_sale_price=" + str(params['MIN_PRICE']) + "&max_sale_price=" + params['MAX_PRICE'] + "&distance_in_km=" +params['DISTANCE']

    query_dict = {
        "source": "search_box",
        "keywords": params['ITEM'],
        "longitude": params['LONGITUDE'],
        "latitude": params['LATITUDE'],
        "order_by": "newest",
        "min_sale_price": params['MIN_PRICE'],
        "max_sale_price": params['MAX_PRICE'],
        "distance_in_km": params['DISTANCE'],
    }
    query_dict = {k: v for k, v in query_dict.items() if v not in ("", "-")}

    base_url = "https://api.wallapop.com/api/v3/search"
    query_string = urlencode(query_dict)
    url = f"{base_url}?{query_string}"


    print(url)
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
        "sec-ch-ua": '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"macOS"'
    }


    response = requests.get(url, headers=headers)
    data = response.json()
    # print(data)
    current_date = datetime.now()
    new_items = []

    for item in data["data"]["section"]["payload"]["items"]:
        title = item["title"]
        description = item["description"]
        price = item["price"]["amount"]
        timestamp = item["modified_at"]
        # user_id = item["user_id"]
        item_url = "https://es.wallapop.com/item/" + item["web_slug"]
        location = item["location"]["postal_code"] + " " + item["location"]["city"] + " " + item["location"]["region2"]
        date = datetime.fromtimestamp(timestamp / 1000)
        difference = current_date - date

        # If item is newer than 2 minutes, print it
        if difference.seconds < REFRESH_TIME:
            new_items.append({'title':title, 'description':description, 'price':price, 'date':date, 'item_url':item_url, 'location':location})
            # print("Item URL: " + item_url)
            # print("Title: " + title)
            # print("Price: " + str(price) + "€")
            # print("Date: " + str(date))
            # print("Description: " + description)
            # print("==========================")
    
    return new_items

def getUserReviews(user_id):
    url = "https://api.wallapop.com/api/v3/users/" + user_id

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


# if __name__ == "__main__":

#     # TELEGRAM_CHAT_ID = get_chat_id()
#     creds = gsheets.googleLogin()

#     while True:

#         for params in gsheets.readSpreadsheet(creds):

#             new_items = search_wallapop()
#             print(new_items)
            
#             if new_items:
#                 for item in new_items:
#                     reviews = getUserReviews(item['user_id'])
#                     message = (
#                         f"<b>{item['title']}</b>\n"
#                         f"<b>Precio:</b> {item['price']}€\n"
#                         # f"<b>Última Modificación:</b> {item[3]}\n"
#                         f"<b>Descripción:</b> {item['description']}\n"
#                         f"<b>Ubicación:</b> {item['location']}\n"
#                         f"<b>URL:</b> <a href='{item['item_url']}'>{item['item_url']}</a>\n\n"
#                     )

#                     print(message)

#                     # send_telegram(message, TELEGRAM_CHAT_ID)
#                 print("Telegram message sent.")
#         time.sleep(REFRESH_TIME)