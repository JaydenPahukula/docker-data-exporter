from datetime import datetime
from collections import defaultdict
import flask
from subprocess import run
import time

BUCKET = "main"



# WARNING incomplete!!!!
def get_hostnames():
    queryString = f"""from(bucket: \"{BUCKET}\")
                       |> range(start:0)
                       |> keep(columns: [\"hostname\"])
                       |> distinct(column: \"hostname\")"""
    completedResponse = run(f"influx query \'{queryString}\'")
    lines = [line.split(",") for line in completedResponse.stdout.decode().split("\r\n")]
    for line in lines:
        print(line)
    return ["test1", "test2"]


def parse_time(s:str):
    # convert UTC ISO time str into unix milliseconds
    tdiff = datetime.utcnow() - datetime.now()
    return int(datetime.timestamp(datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ")) - tdiff.total_seconds()) * 1000


def handle_query(request):
    """
    
    """
    startTime = request["range"]["from"]
    endTime = request["range"]["to"]
    output = []
    for target in request["targets"]:

        # query data from influxdb database
        queryString = f'\'from(bucket: \"{BUCKET}\") |> range(start: {startTime}, stop: {endTime}) |> filter(fn: (r) => r._field==\"{target["target"]}\")\''
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