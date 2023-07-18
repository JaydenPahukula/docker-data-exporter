import datetime
from requests import get
from subprocess import run
import time

BUCKET = "main"

def scrape(ip:str):

    # http get request
    response = get(f"http://{ip}/get-data")
    if response.status_code != 200:
        print(f"Something went wrong while scraping {ip}...\n", response.text)
        return ""

    data = response.json()
    return (f"total-container-count={data['total-container-count']}u,"
            f"running-container-count={data['running-container-count']}u")



def scraper(iplist:list, intervalSeconds:int):

    interval = datetime.timedelta(seconds=intervalSeconds)
    last = datetime.datetime.now() - interval
    
    while 1:
        curr = datetime.datetime.now()
        if curr - interval > last:
            last = curr

            # scrape all data and format
            feilds = [scrape(ip) for ip in iplist]
            unixTime = int(time.mktime(curr.timetuple()))
            datapoints = [f"{iplist[i]} {feilds[i]} {unixTime}" for i in range(len(iplist))]
            
            # write to database
            completedResponse = run(f"influx write --bucket {BUCKET} --precision s \"" + '\n'.join(datapoints) + "\"",
                                    capture_output=True, shell=True)
            if completedResponse.returncode != 0:
                print("Error writing to database\n ", completedResponse.stdout.decode(), "\n ", completedResponse.stderr.decode())
        
        time.sleep(0.01)

    return