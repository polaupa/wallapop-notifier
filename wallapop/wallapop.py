import requests
from datetime import datetime
from urllib.parse import urlencode
import logging

logger = logging.getLogger("wallapop")

def getHeaders():
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
    return headers


def search_wallapop(params, REFRESH_TIME=120):
    logger.info(f"Searching for {params['ITEM']} at {url}")

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
    query_dict = {k: v for k, v in query_dict.items() if str(v) not in ("", "-", "nan", None)}

    base_url = "https://api.wallapop.com/api/v3/search"
    query_string = urlencode(query_dict)
    url = f"{base_url}?{query_string}"
    # logger.info(f'API Endpoint: {url}')
    
    headers = getHeaders()
    response = requests.get(url, headers=headers)
    data = response.json()
    current_date = datetime.now()
    new_items = []

    for item in data["data"]["section"]["payload"]["items"]:
        title = item["title"]
        description = item["description"]
        price = item["price"]["amount"]
        timestamp = item["modified_at"]
        user_id = item["user_id"]
        item_url = "https://es.wallapop.com/item/" + item["web_slug"]
        location = item["location"]["postal_code"] + " " + item["location"]["city"] + " " + item["location"]["region2"]
        date = datetime.fromtimestamp(timestamp / 1000)
        difference = current_date - date

        # If item is newer than REFRESH_TIME seconds, append it
        if difference.seconds < REFRESH_TIME:
            new_items.append({'title':title, 'description':description, 'price':price, 'date':date, 'item_url':item_url, 'location':location, 'user_id': user_id})
    if not new_items:
        logger.info(f"No new items found for {params['ITEM']} :(")
    else:
        logger.info(f"Found {len(new_items)} new items for {params['ITEM']} :)")
    
    return new_items

def getUserReviews(user_id):
    url = f"https://api.wallapop.com/api/v3/users/{user_id}/stats?init=0"

    headers = getHeaders()
    response = requests.get(url, headers=headers)
    data = response.json()

    return data["ratings"][0]["value"]

