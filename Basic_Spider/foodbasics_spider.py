import scrapy
from scrapy.crawler import CrawlerProcess


'''
passwords

root:iamdigital
bot:Iambot123
'''
#keep track of clicked pages
clicked = []
next_link = ""

#Delete current file contenets
open('Basic_Spider/deals.jsonl', 'w').close()

class FlyerSpider(scrapy.Spider):
    name = "flyers"
    start_urls = [
        "https://www.foodbasics.ca/search?sortOrder=relevance&filter=%3Arelevance%3Adeal%3AFLYER_DEAL",
    ]

    def parse(self, response):
        #Set first page as clicked
        clicked.append("1")

        #Get info for each product tile
        for product in response.css("div.default-product-tile"):
            yield {
                "name": product.css("div.head__title::text").get(),
                "price": product.css("span.price-update::text").get(),
                #A bit hacky but some products just don't have a pricing before
                "price_before": product.css("div.pricing__before-price span::text").getall()[1] if len(product.css("div.pricing__before-price span::text").getall())>0 else "",
                "product_id": int(product.css('::attr(data-product-code)').extract()[0]),
                "product_link": "https://www.foodbasics.ca"+product.css("a.product-details-link::attr(href)").extract()[0],
                "product_image": product.css("div.pt__visual picture.defaultable-picture img::attr(src)").get()
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



#Run the spider
if __name__ == "__main__":
    process = CrawlerProcess({
        'USER-AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
        'FEED_FORMAT': 'jsonl',
        'FEED_URI': 'Basic_Spider/deals.jsonl',
        'DOWNLOAD_DELAY': 30
    })

    process.crawl(FlyerSpider)
    process.start()