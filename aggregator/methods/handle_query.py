from datetime import datetime
from collections import defaultdict
import flask
import os
from subprocess import run
import yaml

SERVER_BUCKET = ""
CONTAINER_BUCKET = ""
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))


def get_hostnames():
    # reading config file
    with open(os.path.dirname(CURRENT_DIR) + "/config.yaml", "r") as config_file:
        config = yaml.safe_load(config_file)
    SERVER_BUCKET = config["server-bucket-name"]
    # query database
    queryString = f"""from(bucket: \"{SERVER_BUCKET}\")
                       |> range(start:0)
                       |> keep(columns: [\"hostname\"])
                       |> distinct(column: \"hostname\")"""
    completedResponse = run(f"influx query \'{queryString}\' --raw", capture_output=True, shell=True)
    # parse output
    lines = [line.split(",") for line in completedResponse.stdout.decode().split("\r\n") if line != ""]
    return [line[4] for line in lines[4:]]


def parse_time(s:str):
    # convert UTC ISO time str into unix milliseconds
    tdiff = datetime.utcnow() - datetime.now()
    return int(datetime.timestamp(datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ")) - tdiff.total_seconds()) * 1000


def handle_query(request):
    """
    
    """

    # reading config file
    with open(os.path.dirname(CURRENT_DIR) + "/config.yaml", "r") as config_file:
        config = yaml.safe_load(config_file)
    SERVER_BUCKET = config["server-bucket-name"]
    CONTAINER_BUCKET = config["container-bucket-name"]

    startTime = request["range"]["from"]
    endTime = request["range"]["to"]
    output = []
    for target in request["targets"]:

        # query data from influxdb database
        queryString = f'\'from(bucket: \"{SERVER_BUCKET}\") |> range(start: {startTime}, stop: {endTime}) |> filter(fn: (r) => r._field==\"{target["target"]}\")\''
        completedResponse = run("influx query " + queryString + " --raw", capture_output=True, shell=True)
        if completedResponse.stdout == b'\r\n':
            print("Error, got no data from database")
            return "Error, got no data from database"
        
        # parse lines
        lines = [line.split(",") for line in completedResponse.stdout.decode().split("\r\n")]
        datatype = lines[1][6]

        # timeseries data
        if target["type"] == "timeserie":

            datapoints = defaultdict(lambda: [])
            for line in lines[4:-2]:
                if datatype in ("long", "unsignedLong"):
                    datapoints[line[9]].append([int(line[6]), parse_time(line[5])])
                elif datatype == "boolean":
                    datapoints[line[9]].append([line[6] == "true", parse_time(line[5])])
                else:
                    datapoints[line[9]].append([line[6], parse_time(line[5])])

            for hostname in datapoints.keys():    
                output.append({"target":hostname, "datapoints":datapoints[hostname]})
        
        # table data
        else:
            pass

    return flask.jsonify(output)