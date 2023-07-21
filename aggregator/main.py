from flask import Flask
import os
import sys
import yaml

from methods import scraper

IP_LIST = []
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)


@app.route('/')
def root():
    return "OK"


# prometheus data scrape
@app.route('/metrics')
def metrics():
    metrics = []
    json_data_list = scraper.collectData(IP_LIST)
    for hostname, server_metrics, container_metrics_list in json_data_list:
        # parse server metrics
        for metric in server_metrics:
            if type(server_metrics[metric]) == int:
                metrics.append(f"{metric}{{hostname=\"{hostname}\"}} {server_metrics[metric]}\n")
            else:
                metrics.append(f"{metric}{{hostname=\"{hostname}\",{metric}=\"{server_metrics[metric]}\"}} 1\n")
        
        for container_metrics in container_metrics_list:
            container_name = container_metrics["container_info"]["container_name"]
            
            # parse container info
            container_info = [f"{key}=\"{value}\"" for key, value in container_metrics["container_info"].items()]
            metrics.append(f"container_info{{hostname=\"{hostname}\",{','.join(container_info)}}} 1\n")

            # parse container metrics
            for metric in container_metrics:
                if metric == "container_info": continue
                if type(container_metrics[metric]) == int:
                    metrics.append(f"{metric}{{hostname=\"{hostname}\"}} {container_metrics[metric]}\n")
                else:
                    metrics.append(f"{metric}{{hostname=\"{hostname}\",{metric}=\"{container_metrics[metric]}\"}} 1\n")
    
    print(f"Returned data from {len(json_data_list)} agents")
    return "".join(metrics)



if __name__ == '__main__':
    print("\n\n\n")
    
    print(" * Reading config file")
    with open(CURRENT_DIR + "/aggregator_config.yaml", "r") as config_file:
        config = yaml.safe_load(config_file)
    IP_LIST = config["server-ips"]
    print(f" * Aggregator is configured to read from {len(IP_LIST)} agents")

    port = 5000 # default port
    # getting port argument
    for i in range(len(sys.argv)):
        if (sys.argv[i] == "-p" or sys.argv[i] == "-port") and i + 1 < len(sys.argv):
            try:
                port = int(sys.argv[i + 1])
            except ValueError:
                pass
            break

    app.run(port=port)