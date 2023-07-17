import datetime
import json
from requests import get

def scrape(ip:str, t:datetime.datetime):
    data = get(f"{ip}/get-data")

    return

def scraper(iplist:list, intervalSeconds:int):

    interval = datetime.timedelta(seconds=intervalSeconds)
    last = datetime.datetime.now() - interval
    
    while 1:
        curr = datetime.datetime.now()
        if curr - interval > last:
            last = curr
            for ip in iplist:
                scrape(ip)

    return