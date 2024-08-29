import schedule
import time
import foodbasics_spider as fb_spider
import nofrills_spider as nf_spider
import data_parser

from multiprocessing import Process

def run_fb_spider():
    fb_spider.beginCrawl()

def run_nf_spider():
    nf_spider.beginCrawl()

def run_data_parser():
    data_parser.parseScrapedData()

def collectData():
    #Create separate processes, since scrapy reactors cannot be auto restarted in the same process
    fb_process = Process(target=run_fb_spider)
    nf_process = Process(target=run_nf_spider)
    parser_process = Process(target=run_data_parser)

    fb_process.start()
    nf_process.start()

    #Wait for these to finish first
    fb_process.join()
    nf_process.join()

    #Start and finish parsing data
    parser_process.start()
    parser_process.join()

#Every 30mins
#schedule.every(30).minutes.do(collectData)

#every hour
schedule.every(2).hour.do(collectData)

#Every day 10:30 is like 6:30
#schedule.every().day.at('10:30').do(collectData)

while True:
    schedule.run_pending()
    time.sleep(1)