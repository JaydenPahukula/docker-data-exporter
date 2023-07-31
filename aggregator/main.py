import flask
from flask_cors import cross_origin
import json
import os
from requests import post
import sys
import yaml

from methods import scraper


CONFIG_FILE = "aggregator_config.yaml"
HOSTNAME_FILE = ".known_hostnames"
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

known_containers = {}

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
    # read hostnames file
    known_hostnames = {}
    if os.path.exists(f"{CURRENT_DIR}/{HOSTNAME_FILE}"):
        with open(f"{CURRENT_DIR}/{HOSTNAME_FILE}", "r") as hostname_file:
            raw_file = hostname_file.read()
        if raw_file:
            known_hostnames = json.loads(raw_file)

    metrics = []
    offline_ips = [x for x in ip_list]
    json_data_list = scraper.collectData(ip_list)
    for hostname, server_metrics, container_metrics_list in json_data_list:
        ip = server_metrics["server_ip"]

        # add hostname if not already known
        if ip not in known_hostnames: known_hostnames[ip] = hostname

        # remove ip from offline list
        offline_ips.remove(ip)
        metrics.append(f"server_online{{hostname=\"{hostname}\"}} 1\n")

        # parse server metrics
        for metric in server_metrics:
            if type(server_metrics[metric]) == int:
                metrics.append(f"{metric}{{hostname=\"{hostname}\"}} {server_metrics[metric]}\n")
            else:
                metrics.append(f"{metric}{{hostname=\"{hostname}\",{metric}=\"{server_metrics[metric]}\"}} 1\n")
        
        for container_metrics in container_metrics_list:
            container_name = container_metrics["container_info"]["container_name"]

            # add/update known_containers
            known_containers[container_name] = ip
            
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

    # any ip still here is offline/unreachable
    for ip in offline_ips:
        if ip in known_hostnames:
            hostname = known_hostnames[ip]
            metrics.append(f"server_online{{hostname=\"{hostname}\"}} 2\n")

    # write known hostnames
    with open(HOSTNAME_FILE, "w") as hostname_file:
        hostname_file.write(json.dumps(known_hostnames))

    print(f"Returned data from {len(json_data_list)} agents")
    return "".join(metrics)

@app.route("/command/<cmd_str>", methods=["POST"])
@cross_origin()
def handleCommands(cmd_str="no command given"):
    print("Received request:", cmd_str)
    container_list = flask.request.data.decode().strip("}").strip("{").split(",")

    output = ""
    failed = False
    for container in container_list:
        if container in known_containers:
            ip = known_containers[container]
            response = post(f"http://{ip}/command/{cmd_str}?container={container}")
            if response.status_code in (200, 204):
                output += f"  {container} -> success\n"
            else:
                output += f"  {container} -> failed: {response.text}\n"
                failed = True
        else:
            output += f"  {container} -> couldn't find ip address\n"
            failed = True
    
    print(output, end="")
    response = flask.make_response(output)
    if failed: response.status_code = 500
    else:      response.status_code = 200
    response.headers["Access-Control-Allow-Credentials"] = "true"
    return response


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

    app.run(port=port, host="0.0.0.0")