import schedule
import time
import foodbasics_spider as fb_spider
import nofrills_spider as nf_spider
import data_parser


def collectData():
    fb_spider.beginCrawl()
    nf_spider.beginCrawl()
    data_parser.parseScrapedData()

#Every 30mins
#schedule.every(30).minutes.do(collectData)

#Every day
schedule.every().day.at('10:30').do(collectData)

while True:
    schedule.run_pending()
    time.sleep(1)