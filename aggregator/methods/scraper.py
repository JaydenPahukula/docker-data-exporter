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


def parseServerData(ip: str, data: dict) -> dict:

    output = f"{ip},hostname={data['hostname']} docker-running={data['docker-running']}"
    output = {
        "server_ip": ip,
        "server_hostname": data['hostname'],
        "server_agent_running": 1,
        "server_docker_running": int(data['docker-running']),
    }
    if data['docker-running']:
        output.update({
            "server_docker_version": data["docker-version"],
            "server_swarm_mode": int(data["swarm-mode"]),
            "server_image_count": data["image-count"],
            "server_total_container_count": data["total-container-count"],
            "server_running_container_count": data["running-container-count"]
        })
    return output

def parseContainerData(ip: str, data: dict) -> list:
    if not data['docker-running']:
        return []
    
    output_arr = []
    for container in data["containers"]:
        container_output = {
            "container_info": {
                "container_id": container["id"],
                "container_name": container["name"],
                "container_image": container["image"],
                "container_image_label": container["image-label"],
                "container_user": container["user"],
                "container_creation_time": datetime.fromtimestamp(container["created-at"]).isoformat(sep=" "),
            },
            "container_state": container["state"],
            "container_cpu_percent": container["cpu-percent"],
            "container_mem_percent": container["mem-percent"],
            "container_network_bytes_in": container["network-bytes-in"],
            "container_network_bytes_out": container["network-bytes-out"],
            "container_block_bytes_in": container["block-bytes-in"],
            "container_block_bytes_out": container["block-bytes-out"],
        }
        output_arr.append(container_output)
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
    output_arr = []
    for i in range(len(ip_list)):
        if raw_data[i] == None: continue

        server_data = parseServerData(ip_list[i], raw_data[i])
        container_data = parseContainerData(ip_list[i], raw_data[i])
        output_arr.append((raw_data[i]["hostname"], server_data, container_data))
    

    return output_arr

if __name__ == "__main__":
    print("\n\n\nScraping:")
    output = collectData(config["server-ips"])
    print("Output:", output)