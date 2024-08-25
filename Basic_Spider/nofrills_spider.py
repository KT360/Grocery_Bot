import requests
import json
import time

url = "https://api.pcexpress.ca/pcx-bff/api/v1/products/deals"

# Initial payload for the first page
payload = {
    "banner": "nofrills",
    "cartId": "2e0b186a-874d-4f19-91ce-fbaad4bef37f",
    "date": "21082024",
    "lang": "en",
    "offerType": "ALL",
    "pagination": {"from": 1, "size": 48},
    "pcId": None,
    "pickupType": "STORE",
    "storeId": "3152"
}

headers = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "en",
    "Business-User-Agent": "PCXWEB",
    "Connection": "keep-alive",
    "Content-Length": "201",
    "Content-Type": "application/json",
    "Host": "api.pcexpress.ca",
    "Origin": "https://www.nofrills.ca",
    "Origin_Session_Header": "B",
    "Referer": "https://www.nofrills.ca/",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "cross-site",
    "Site-Banner": "nofrills",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
    "is-helios-account": "false",
    "sec-ch-ua": "'Not)A;Brand';v='99', 'Google Chrome';v='127', 'Chromium';v='127'",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "Windows",
    "x-apikey": "C1xujSegT5j3ap3yexJjqhOfELwGKYvz"
}
"name, price, price_before, product_link, product_id, product_image"

# Make the POST request
# Let's just go through 20 pages, seems fine for now
def beginCrawl():

    print('nf_spider STARTING REQUESTS')

    #Truncate content in current file if present
    open('Basic_Spider/nofrills_deals.jsonl', 'w').close()

    for i in range(1,21):

        payload['pagination']['from'] = i

        response = requests.post(url, json=payload, headers=headers)

        if response.status_code == 200:
            product_list = response.json()['results']

            with open('Basic_Spider/nofrills_deals.jsonl', 'a') as f:
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

        print('nf_spider REQUEST #'+str(i)+' FINISHED.')
        #Send request every 30s
        time.sleep(30)
