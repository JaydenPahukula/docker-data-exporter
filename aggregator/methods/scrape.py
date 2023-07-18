from datetime import datetime
from requests import get
from subprocess import run
import threading
import time

BUCKET = "main"

def scrape(ip:str) -> str:

    # http get request
    response = get(f"http://{ip}/get-data")
    if response.status_code != 200:
        print(f"Something went wrong while scraping {ip}...\n", response.text)
        return ""

    data = response.json()
    print(data)
    queryString = f"{ip},hostname={data['hostname']} docker-running={data['docker-running']}"
    if data['docker-running']:
        queryString += f",docker-version=\"{data['docker-version']}\""
        queryString += f",swarm-mode={data['swarm-mode']}"
        queryString += f",image-count={data['image-count']}"
        queryString += f",total-container-count={data['total-container-count']}"
        queryString += f",running-container-count={data['running-container-count']}"
    
    return queryString


def scrape_wrapper(ip:str, data_arr:list, index:int) -> None:
    data_arr[index] = scrape(ip)


def scraper(ip_list:list, interval_seconds:int) -> None:
    while True:
        start_time = datetime.now()

        # scrape all data and format
        data = [None] * len(ip_list)
        scraper_threads = []
        # starting all scraper threads
        for i in range(len(ip_list)):
            new_thread = threading.Thread(target=scrape_wrapper, args=(ip_list[i], data, i))
            scraper_threads.append(new_thread)
            new_thread.start()
        
        # waiting for scraper threads to complete
        for i in range(len(scraper_threads)):
            scraper_threads[i].join()

        unix_time = int(time.mktime(datetime.now().timetuple()))
        query_strings = [f"{data[i]} {unix_time}" for i in range(len(ip_list))]
        
        # write to database
        completed_response = run(f"influx write --bucket {BUCKET} --precision s \"" + '\n'.join(query_strings) + "\"",
                                capture_output=True, shell=True)
        if completed_response.returncode != 0:
            print("Error writing to database\n ", completed_response.stdout.decode(), "\n ", completed_response.stderr.decode())
        
        run_time = (datetime.now() - start_time).total_seconds()
        time.sleep(interval_seconds - run_time)

    return