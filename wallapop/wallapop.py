import requests
from datetime import datetime
from urllib.parse import urlencode
import logging
import json
from time import sleep
from wallapop.db import insert_items

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


def search_wallapop(params, REFRESH_TIME=120, MOCK=False):
    REFRESH_TIME = REFRESH_TIME + 5
    if MOCK:
        logger.warning("Using mock data for search_wallapop")
        with open('wallapop/piano-wallapop.json', 'r') as f:
            data = json.load(f)
    else:
        query_dict = {
            "source": "search_box",
            "keywords": params['ITEM'],
            "longitude": params['LONGITUDE'],
            "latitude": params['LATITUDE'],
            "order_by": "newest",
            "min_sale_price": params['MIN_PRICE'],
            "max_sale_price": params['MAX_PRICE'],
            "distance_in_km": int(params['DISTANCE']) if str(params['DISTANCE']) not in ("", "-", "nan", None) else "-",
        }
        query_dict = {k: v for k, v in query_dict.items() if str(v) not in ("", "-", "nan", None)}

        base_url = "https://api.wallapop.com/api/v3/search"
        query_string = urlencode(query_dict)
        url = f"{base_url}?{query_string}"
        logger.debug(f"Searching for {params['ITEM']} at https://es.wallapop.com/search?{query_string}")

        # logger.info(f'API Endpoint: {url}')
        
        headers = getHeaders()
        response = requests.get(url, headers=headers)
        try:
            data = response.json()
        except Exception as e:
            logger.error(f"Error parsing JSON response: {e}")
            logger.error(f"Response content: {response.content}")
            return []
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
        user_reviews = getUserReviews(user_id)
        images = []
        for image in item["images"]:
            images.append(image["urls"]['small'])

        # If item is newer than REFRESH_TIME seconds, append it
        if MOCK:
            new_items.append({'title': title, 'description': description, 'price': price, 'date': date, 'item_url': item_url, 'location': location, 'user_id': user_id, 'images': images, 'user_reviews': user_reviews})
        elif difference.seconds < REFRESH_TIME + 120:
            new_items.append({'title':title, 'description':description, 'price':price, 'date':date, 'item_url':item_url, 'location':location, 'user_id': user_id, 'user_reviews': user_reviews})
    if new_items:
        logger.info(f"Found {len(new_items)} new items for {params['ITEM']} :)")
        new_items = insert_items(tablename = params['ITEM'], items = new_items)

    return new_items

def getUserReviews(user_id):
    #reviews
    url = f"https://api.wallapop.com/api/v3/users/{user_id}/stats?init=0"
    #stats
    # url = "https://api.wallapop.com/api/v3/users/{user_id}/"
    #extra-info
    # url = "https://api.wallapop.com/api/v3/users/{user_id}/extra-info"

    headers = getHeaders()
    response = requests.get(url, headers=headers)
    try:
        data = response.json()
    except requests.exceptions.JSONDecodeError as e:
        logger.error(f"Error parsing JSON response for user {user_id}: {e}")
        logger.error(f"Response content: {response.content}")
        return -1
    try:
        ratings = data["ratings"][0]["value"]
    except (KeyError, IndexError) as e:
        logger.error(f"Error extracting ratings for user {user_id}: {e}")
        logger.error(f"Response data: {data}")
        return 80

    
    return ratings

