import flask
import os
import sys
import yaml

from methods import scraper


CONFIG_FILE = "aggregator_config.yaml"
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

app = flask.Flask(__name__)


@app.route('/')
def root():
    return "OK\n"


@app.route('/add-agent', methods=["POST"])
def addagent():
    ip = flask.request.remote_addr
    port = flask.request.args.get("port")
    if port: ip += ":" + port

    # read file
    config = None
    with open(CONFIG_FILE, "r") as config_file:
        config = yaml.safe_load(config_file)
    
    # add ip address
    if "server-ips" in config:
        ip_set = set(config["server-ips"])
        ip_set.add(ip)
        config["server-ips"] = sorted(list(ip_set))
    else:
        config["server-ips"] = [ip]

    # write file
    with open(CONFIG_FILE, "w") as config_file:
        config_file.write(
            "---\n" +
            "# list of IP addresses to scrape\n" + 
            yaml.dump(config) +
            "...\n")
    
    return f"Successfully added agent {ip}\n"


# prometheus data scrape
@app.route('/metrics', methods=["GET"])
def metrics():
    # read config file
    with open(CONFIG_FILE, "r") as config_file:
        config = yaml.safe_load(config_file)
    ip_list = config["server-ips"]

    metrics = []
    json_data_list = scraper.collectData(ip_list)
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
                    metrics.append(f"{metric}{{hostname=\"{hostname}\",container_name=\"{container_name}\"}} {container_metrics[metric]}\n")
                else:
                    metrics.append(f"{metric}{{hostname=\"{hostname}\",container_name=\"{container_name}\",{metric}=\"{container_metrics[metric]}\"}} 1\n")
    
    print(f"Returned data from {len(json_data_list)} agents")
    return "".join(metrics)



if __name__ == '__main__':
    print("\n\n\n")

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