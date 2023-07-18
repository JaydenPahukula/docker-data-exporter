from datetime import datetime, timedelta
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



def scraper(ip_list:list, interval_seconds:int):
    
    while True:
        start_time = datetime.now()

        # scrape all data and format
        feilds = [scrape(ip) for ip in ip_list]
        unix_time = int(time.mktime(datetime.now().timetuple()))
        datapoints = [f"{ip_list[i]} {feilds[i]} {unix_time}" for i in range(len(ip_list))]
        
        # write to database
        completed_response = run(f"influx write --bucket {BUCKET} --precision s \"" + '\n'.join(datapoints) + "\"",
                                capture_output=True, shell=True)
        if completed_response.returncode != 0:
            pass#print("Error writing to database\n ", completed_response.stdout.decode(), "\n ", completed_response.stderr.decode())
        
        run_time = (datetime.now() - start_time).total_seconds()
        time.sleep(interval_seconds - run_time)

    return