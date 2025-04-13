#link: https://www.walmart.ca/en/shop/weekly-flyer-features/6000196190101?catId=10019&icid=cp_l1_page_grocery_lhn_weekly_flyer_58867_Y2KZC3NLT5&facet=fulfillment_method_in_store%3AIn+Store

import scrapy
from scrapy.crawler import CrawlerProcess
import os
import json
import math

def safe_float_cast(value):
    try:
        return float(value)
    except (ValueError, TypeError):
        return None

def safe_int_cast(value):
    try:
        return int(value)
    except (ValueError, TypeError):
        return None


#check function to prevent the program from simply crashing if a null value is provided
def safe_value_check(value, arr_index=None):
    
    if arr_index:
        if len(value) > 0:
            return value[arr_index]
    else:
        if value:
            return value
        else:
            return None

#Get proxy
username = os.getenv('PROXY_NAME')
password = os.getenv('PROXY_PASSWORD')
host = os.getenv('PROXY_HOST')

proxy = "http://{}:{}@{}:6060".format(username,password,host)


class TestSpider(scrapy.Spider):
    name = "test"
    total_count = 0
    page_numb = 1
    total_pages = 0

    #keep track of clicked pages
    clicked = []
    next_link = ""

    def start_requests(self):
        request = scrapy.Request(url="https://www.walmart.ca/en/shop/weekly-flyer-features/6000196190101?catId=10019&icid=cp_l1_page_grocery_lhn_weekly_flyer_58867_Y2KZC3NLT5&facet=fulfillment_method_in_store%3AIn+Store", callback=self.parse)
        request.meta['proxy'] = proxy
        yield request
    
    def parse(self, response):

        text_data = response.css("script#__NEXT_DATA__::text").get()
        json_data = json.loads(text_data)
        product_list = json_data['props']['pageProps']['initialData']['searchResult']['itemStacks'][0]['items']
        
        if self.page_numb == 1:
            self.total_count = json_data['props']['pageProps']['initialData']['searchResult']['aggregatedCount']
            #Assuming maximum number of items to be 40
            self.total_pages = math.ceil(self.total_count/40)

        for product in product_list:
            if 'name' in product:
                yield {
                    #Key error at name for some reason
                    "name": product['name'],
                    "price": safe_float_cast(product['priceInfo']['linePrice'].replace('$','')),
                    "price_before": safe_float_cast(product['priceInfo']['wasPrice'].replace('$','')),
                    "product_id": safe_int_cast(product['id']),
                    "product_link": "https://www.walmart.ca/"+product['canonicalUrl'],
                    "product_image": safe_value_check(product['imageInfo']['thumbnailUrl'])
                }
        self.page_numb += 1
        if self.page_numb < self.total_pages:
            yield scrapy.Request(url="https://www.walmart.ca/en/shop/weekly-flyer-features/6000196190101?catId=10019&icid=cp_l1_page_grocery_lhn_weekly_flyer_58867_Y2KZC3NLT5&facet=fulfillment_method_in_store%3AIn+Store&page="+str(self.page_numb), meta={'proxy':proxy},callback=self.parse)
        


def beginCrawl():
    process = CrawlerProcess({
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
        'FEED_FORMAT': 'jsonl',
        'FEED_URI': 'walmart_deals.jsonl',
        'RETRY_HTTP_CODES': [500, 502, 503, 504, 522, 524, 408, 429, 403,307],
        'RETRY_TIMES': 4,
        'DOWNLOAD_DELAY': 30
    })

    #Delete current file contenets
    open('walmart_deals.jsonl', 'w').close()

    process.crawl(TestSpider)
    process.start()