from datetime import datetime
import flask
from subprocess import run
import time

BUCKET = "main"

def parseTime(s:str):
    # convert UTC ISO time str into unix milliseconds
    tdiff = datetime.utcnow() - datetime.now()
    return int(datetime.timestamp(datetime.strptime(s, "%Y-%m-%dT%H:%M:%S.000000000Z")) - tdiff.total_seconds())*1000

def handle_query(request):
    """
    
    """
    print("Received query")
    startTime = request["range"]["from"]
    endTime = request["range"]["to"]
    output = []
    for target in request["targets"]:
        queryString = f'\'from(bucket: \"{BUCKET}\") |> range(start: {startTime}, stop: {endTime}) |> filter(fn: (r) => r._field==\"{target["target"]}\")\''
        completedResponse = run("influx query " + queryString, capture_output=True, shell=True)
        print(completedResponse.stdout.decode())
        print(completedResponse.stderr.decode())
        lines = completedResponse.stdout.decode().split("\n")
        while not lines[0]: lines.pop(0)
        for line in lines:
            print(line.split())
        datatype = lines[2].split()[-1][7:]
        if target["type"] == "timeserie":
            datapoints = []
            if datatype in ("int", "uint"):
                datapoints = [[int(line.split()[-1]), parseTime(line.split()[-2])] for line in lines[4:-1]]
            elif datatype == "bool":
                datapoints = [[line.split()[-1] == "true", parseTime(line.split()[-2])] for line in lines[4:-1]]
            else:
                datapoints = [[line.split()[-1], parseTime(line.split()[-2])] for line in lines[4:-1]]
            output.append({"target":target["target"], "datapoints":datapoints})

    return flask.jsonify(output)