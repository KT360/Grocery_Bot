import requests
import json
import time
import math

url = "https://api.pcexpress.ca/pcx-bff/api/v1/products/deals"

# Initial payload for the first page
payload = {
    "banner": "superstore",
    "cartId": "a673aaa6-5fc6-4217-9ead-86d6c35bb3b9",
    "lang": "en",
    "offerType": "ALL",
    "pagination": {"from": 0, "size": 48},
    "pcId": None,
    "pickupType": "STORE",
    "storeId": "2827"
}

headers = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "en",
    "Business-User-Agent": "PCXWEB",
    "Connection": "keep-alive",
    "Content-Length": "203",
    "Content-Type": "application/json",
    "Host": "api.pcexpress.ca",
    "Origin": "https://www.realcanadiansuperstore.ca",
    "Origin_Session_Header": "B",
    "Referer": "https://www.realcanadiansuperstore.ca/",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "cross-site",
    "Site-Banner": "superstore",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
    "is-helios-account": "false",
    "sec-ch-ua": "'Not)A;Brand';v='99', 'Google Chrome';v='127', 'Chromium';v='127'",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "Windows",
    "x-apikey": "C1xujSegT5j3ap3yexJjqhOfELwGKYvz"
}
"name, price, price_before, product_link, product_id, product_image"

def scrapProducts(product_list):
    with open('superstore_deals.jsonl', 'a') as f:
        for product in product_list:
            data = {"product_id": int(product['articleNumber']), 
                    "name":product['name'], 
                    "price":float(product['prices']['price']['value']), 
                    "price_before":float(product['prices']['wasPrice']['value']) if product['prices']['wasPrice'] else None,  #Sometimes there is not price before
                    "product_link":'https://www.nofrills.ca/'+product['link'], 
                    "product_image":product['imageAssets'][0]['mediumUrl']
                    }
            entry = json.dumps(data)+'\n'
            f.write(entry)

# Make the POST request
def beginCrawl():

    #Default number of pages to go through
    total_pages = 20
    page_size = 48

    print('SUPERSTORE_spider STARTING REQUESTS')

    #Truncate content in current file if present
    open('superstore_deals.jsonl', 'w').close()

    #Send initial request to get first batch and total number of pages
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        json_response = response.json()
        total_results = json_response['pagination']['totalResults']
        total_pages = math.ceil(total_results/page_size)
        product_list = json_response['results']
        scrapProducts(product_list=product_list)


    #Wait a couple of seconds
    time.sleep(10)

    #Go through rest of pages
    for i in range(1,total_pages):

        payload['pagination']['from'] = i

        response = requests.post(url, json=payload, headers=headers)

        if response.status_code == 200:
            product_list = response.json()['results']
            scrapProducts(product_list=product_list)

        print('SUPERSTORE_spider REQUEST #'+str(i)+' FINISHED.')
        #Send request every 30s
        time.sleep(30)
