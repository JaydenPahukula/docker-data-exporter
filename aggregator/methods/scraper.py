from datetime import datetime
import os
import requests
from subprocess import run
import threading
import time
import yaml

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
# reading config file
with open(os.path.dirname(CURRENT_DIR) + "/aggregator_config.yaml", "r") as config_file:
    config = yaml.safe_load(config_file)
SERVER_BUCKET = config["server-bucket-name"]
CONTAINER_BUCKET = config["container-bucket-name"]

def scrape(ip: str):

    # http get request
    try:
        response = requests.get(f"http://{ip}/get-data")
    except requests.exceptions.ConnectionError:
        print(f"Couldn't connect to agent at {ip}")
        return None
    if response.status_code != 200:
        print(f"Something went wrong while scraping {ip}:\n", response.text)
        return None

    return response.json()

def scrapeWrapper(ip:str , data_arr: list, index: int) -> None:
    data_arr[index] = scrape(ip)


def parseServerData(ip: str, data: dict) -> str:

    output = f"{ip},hostname={data['hostname']} docker-running={data['docker-running']}"
    if data['docker-running']:
        output += f",docker-version=\\\"{data['docker-version']}\\\""
        output += f",swarm-mode={data['swarm-mode']}"
        output += f",image-count={data['image-count']}u"
        output += f",total-container-count={data['total-container-count']}u"
        output += f",running-container-count={data['running-container-count']}u"
    return output

def parseContainerData(ip: str, data: dict) -> list:

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
        
        output_arr.append(f"{container['name']},hostname={data['hostname']} {','.join(fields)}")
    return output_arr

def collectData(ip_list: list):

    raw_data = [None] * len(ip_list)
    scraper_threads = []
    # starting scraper threads
    for i in range(len(ip_list)):
        new_thread = threading.Thread(target=scrapeWrapper, args=(ip_list[i], raw_data, i))
        scraper_threads.append(new_thread)
        new_thread.start()
    
    # waiting for scraper threads to complete
    for i in range(len(scraper_threads)):
        scraper_threads[i].join()
    
    # parsing data
    parsed_data = []
    for i in range(len(ip_list)):
        if raw_data[i] == None: continue
        parsed_server_data = parseServerData(ip_list[i], raw_data[i])
        parsed_container_data = parseContainerData(ip_list[i], raw_data[i])
        parsed_data.append((raw_data[i]["hostname"], parsed_server_data, parsed_container_data))
    

    return parsed_data

if __name__ == "__main__":
    print("\n\n\nScraping:")
    output = collectData(config["server-ips"])
    print("Output:", output)