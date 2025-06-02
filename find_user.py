import requests

# url = "https://api.wallapop.com/api/v3/search?source=search_box&keywords=" + "raspberry" + "&longitude=" + "2.1699187" + "&latitude=" + "41.38791" + "&order_by=newest&min_sale_price=" + str(0) + "&max_sale_price=" + str(100) + "&distance_in_km=" + str(30)

#me
url = "https://api.wallapop.com/api/v3/users/p61o484n1xj5/stats?init=0"
#stats
url = "https://api.wallapop.com/api/v3/users/p61o484n1xj5/"
#extra-info
url = "https://api.wallapop.com/api/v3/users/p61o484n1xj5/extra-info"
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
    "sec-ch-ua": '"Google Chrome";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"'
}


response = requests.get(url, headers=headers)
data = response.json()

print(data)
# current_date = datetime.now()
# new_items = []

# for item in data["data"]["section"]["payload"]["items"]:
#     title = item["title"]
#     description = item["description"]
#     price = item["price"]["amount"]
#     timestamp = item["modified_at"]
#     item_url = "https://es.wallapop.com/item/" + item["web_slug"]
#     location = item["location"]["postal_code"] + " " + item["location"]["city"] + " " + item["location"]["region2"]
#     date = datetime.fromtimestamp(timestamp / 1000)
#     difference = current_date - date

#     # If item is newer than 2 minutes, print it
#     if difference.seconds < REFRESH_TIME:
#         new_items.append({'title':title, 'description':description, 'price':price, 'date':date, 'item_url':item_url, 'location':location})
#         # print("Item URL: " + item_url)
#         # print("Title: " + title)
#         # print("Price: " + str(price) + "€")
#         # print("Date: " + str(date))
#         # print("Description: " + description)
#         # print("==========================")

