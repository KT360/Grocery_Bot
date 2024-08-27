from typing import Iterable
import scrapy
from scrapy.crawler import CrawlerProcess

#TODO: The program throws an error at the end of the craw because next link is null
#Added a check, stil doesn't work. Scrapy is asynchronous. Need to find a way to make it check next_link before

#keep track of clicked pages
clicked = []
next_link = ""


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
        

#Delete current file contenets
open('foodbasics_deals.jsonl', 'w').close()

class FlyerSpider(scrapy.Spider):
    name = "flyers"

    #start_urls = ["https://www.foodbasics.ca/search?sortOrder=relevance&filter=%3Arelevance%3Adeal%3AFLYER_DEAL"]
    
    #NOTE MAKE PROXY AN ENVIRONEMENT VARIABLE LATER IF WORKS
    def start_requests(self):
        request = scrapy.Request(url="https://www.foodbasics.ca/search?sortOrder=relevance&filter=%3Arelevance%3Adeal%3AFLYER_DEAL", callback=self.parse)
        request.meta['proxy'] = "http://wl605c9imiopiy3-country-ca:zvkqohsjntt7yvr@rp.proxyscrape.com:6060"
        yield request
    
    def parse(self, response):
        #Set first page as clicked
        clicked.append("1")

        #Get info for each product tile
        for product in response.css("div.default-product-tile"):
            #name
            name = safe_value_check(product.css("div.head__title::text").get())
            #price
            price = safe_float_cast(safe_value_check(product.css("span.price-update::text").get().replace('$','')))
            
            #Price Before
            price_before = None
            temp = safe_value_check(product.css("div.pricing__before-price span::text").getall(),arr_index=1)
            if temp:
                price_before = safe_float_cast(temp.replace('$',''))


            product_id = None            
            temp = safe_value_check(product.css('::attr(data-product-code)').extract(), arr_index=0)
            if temp:
                product_id = safe_int_cast(temp[0])
            
            #Product_link
            product_link = ""
            temp = safe_value_check(product.css("a.product-details-link::attr(href)"), arr_index=0)
            if temp:
                product_link = "https://www.foodbasics.ca"+temp.get()

            #GEt the firstt 'picture' tag, the grab the second set image link, that's the big one
            product_image = ""
            temp = safe_value_check(product.css("div.pt__visual picture.defaultable-picture source::attr(srcset)").getall(), arr_index=0)
            if temp:
                product_image = str(temp).split(' ')[1]

            yield {
                "name": name,
                "price": price,
                "price_before": price_before,
                "product_id": product_id,
                "product_link": product_link,
                "product_image": product_image
            }

        #For each pagination linkn, check if page has already been clicked, and make sure the link only contains 'ppn--element' as it's class
        for page_link in response.css("div.ppn--pagination a.ppn--element"):
            
            page_number = page_link.css("::text").get()
            print("PAGE NUMBER: "+page_number)

            if page_link.attrib.get('class') == 'ppn--element':
                if page_number and not(page_number == "...") and  not(page_number in clicked):
                    next_link = page_link.css("::attr(href)").extract()[0]
                    print("NEXT LINK: "+ next_link)
                    clicked.append(page_number)
                    break
        
        if next_link:
            yield scrapy.Request(url="https://www.foodbasics.ca"+next_link, callback=self.parse)


def beginCrawl():
    process = CrawlerProcess({
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
        'FEED_FORMAT': 'jsonl',
        'FEED_URI': 'foodbasics_deals.jsonl',
        'DOWNLOAD_DELAY': 30
    })

    process.crawl(FlyerSpider)
    process.start()


beginCrawl()