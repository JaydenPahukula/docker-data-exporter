from datetime import datetime
import os
from requests import get, exceptions
from subprocess import run
import threading
import time
import yaml

SERVER_BUCKET = ""
CONTAINER_BUCKET = ""
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

def scrape(ip:str):

    # http get request
    try:
        response = get(f"http://{ip}/get-data")
    except exceptions.ConnectionError:
        print(f"Couldn't connect to agent at {ip}")
        return None
    if response.status_code != 200:
        print(f"Something went wrong while scraping {ip}:\n", response.text)
        return None

    return response.json()

def scrapeWrapper(ip:str, data_arr:list, index:int) -> None:
    data_arr[index] = scrape(ip)


def parseServerData(ip:str, data:dict, timestamp:int) -> str:

    output = f"{ip},hostname={data['hostname']} docker-running={data['docker-running']}"
    if data['docker-running']:
        output += f",docker-version=\\\"{data['docker-version']}\\\""
        output += f",swarm-mode={data['swarm-mode']}"
        output += f",image-count={data['image-count']}u"
        output += f",total-container-count={data['total-container-count']}u"
        output += f",running-container-count={data['running-container-count']}u"
    return output + " " + str(timestamp)

def parseContainerData(ip:str, data:dict, timestamp:int) -> list:

    output_arr = []
    for container in data["containers"]:
        if not data['docker-running']:
            continue
        
        # adding container data to fields
        fields = []
        for key, val in container.items():
            # skipping container name
            if key == "name":
                continue

            field = f"{key}="
            if type(val) == str:
                field += "\\\"" + val + "\\\""
            elif type(val) == int:
                field += str(val) + "u"
            else:
                field += str(val)

            fields.append(field)
        
        output_arr.append(f"{container['name']},hostname={data['hostname']} {','.join(fields)} {timestamp}")
    return output_arr


def scraper(ip_list:list, interval_seconds:int) -> None:

    # reading config file
    with open(os.path.dirname(CURRENT_DIR) + "/config.yaml", "r") as config_file:
        config = yaml.safe_load(config_file)
    SERVER_BUCKET = config["server-bucket-name"]
    CONTAINER_BUCKET = config["container-bucket-name"]

    while True:
        start_time = datetime.now()
        timestamp = int(time.mktime(datetime.now().timetuple()))

        server_data = [None] * len(ip_list)
        scraper_threads = []
        # starting scraper threads
        for i in range(len(ip_list)):
            new_thread = threading.Thread(target=scrapeWrapper, args=(ip_list[i], server_data, i))
            scraper_threads.append(new_thread)
            new_thread.start()
        
        # waiting for scraper threads to complete
        for i in range(len(scraper_threads)):
            scraper_threads[i].join()
        
        # parsing server data
        parsed_server_data = []
        for i in range(len(ip_list)):
            if server_data[i] == None: continue
            parsed_server_data.append(parseServerData(ip_list[i], server_data[i], timestamp))

        # writing to server database
        completed_response = run(f"influx write --bucket {SERVER_BUCKET} --precision s \"" + '\n'.join(parsed_server_data) + "\"",
                                capture_output=True, shell=True)
        if completed_response.returncode != 0:
            print("Error writing to server database\n ", completed_response.stdout.decode(), "\n ", completed_response.stderr.decode())
        else:
            print(f"Wrote data from {len(parsed_server_data)} agents")
        
        # parsing container data
        parsed_container_data = []
        for i in range(len(ip_list)):
            if server_data[i] == None: continue
            parsed_container_data += parseContainerData(ip_list[i], server_data[i], timestamp)

        # writing to container database
        completed_response = run(f"influx write --bucket {CONTAINER_BUCKET} --precision s \"" + '\n'.join(parsed_container_data) + "\"",
                                capture_output=True, shell=True)
        if completed_response.returncode != 0:
            print("Error writing to container database\n ", completed_response.stdout.decode(), "\n ", completed_response.stderr.decode())
        else:
            print(f"Wrote data from {len(parsed_container_data)} containers")

        run_time = (datetime.now() - start_time).total_seconds()
        time.sleep(interval_seconds - run_time)

    return