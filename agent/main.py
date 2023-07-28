from datetime import datetime
import flask
import json
import sys

from methods.subprocess_run import subprocessRun
from methods.parse_units import parseByteUnits

app = flask.Flask(__name__)


@app.route('/')
def root():
    return "OK"

@app.route('/get-data')
def getData():
    output = {}

    # getting hostname
    completed_command = subprocessRun("hostname")
    output["hostname"] = completed_command.stdout.decode().strip()

    # checking if docker is running
    completed_command = subprocessRun("systemctl is-active docker")
    docker_running = completed_command.stdout.decode().strip() == "active"
    output["docker-running"] = docker_running
    if not docker_running:
        return flask.make_response(json.dumps(output), 200)
  
    # getting docker version
    completed_command = subprocessRun("docker --version")
    docker_version = completed_command.stdout.decode().strip()[15:]
    docker_version = docker_version.replace(", ", " (", 1) + ")"
    output["docker-version"] = docker_version

    # getting docker info
    completed_command = subprocessRun("docker info --format json")
    docker_info = json.loads(completed_command.stdout.decode())

    output["swarm-mode"] = docker_info["Swarm"]["LocalNodeState"] == "active"
    output["image-count"] = docker_info["Images"]
    output["total-container-count"] = docker_info["Containers"]
    output["running-container-count"] = docker_info["ContainersRunning"]

    # getting specific container info
    output["containers"] = []
    completed_command = subprocessRun("docker ps -a --format json")
    statuses = completed_command.stdout.decode().split("\n")
    statuses = [json.loads(s) for s in statuses if s != ""]
    for status in statuses:
        container_output = {
            "id": status['ID'],
            "name": status["Names"],
            "image": status["Image"],
            "image-label": status["Labels"],
            "user": status["Names"].split("--")[-1],
            "state": status["State"],
            "status": status["Status"]
        }

        created_at = datetime.strptime(status["CreatedAt"], "%Y-%m-%d %H:%M:%S %z %Z")
        container_output["created-at"] = round(created_at.timestamp())

        completed_command = subprocessRun("docker stats --no-stream --format json " + status["ID"])
        container_stats = json.loads(completed_command.stdout.decode())
        
        network_in, network_out = (parseByteUnits(x) for x in container_stats["NetIO"].split(" / "))
        block_in, block_out = (parseByteUnits(x) for x in container_stats["BlockIO"].split(" / "))
        
        container_output.update({
            "cpu-percent": float(container_stats["CPUPerc"][:-1]),
            "mem-percent": float(container_stats["MemPerc"][:-1]),
            "network-bytes-in": network_in,
            "network-bytes-out": network_out,
            "block-bytes-in": block_in,
            "block-bytes-out": block_out
        })

        completed_command = subprocessRun("docker stats --no-stream --format json " + status["ID"])
        container_stats = json.loads(completed_command.stdout.decode())

        output["containers"].append(container_output)


    return flask.make_response(json.dumps(output) + "\n", 200)


@app.route("/command/<cmd_str>", methods=["POST"])
def handleCommands(cmd_str="no command given"):
    container_name = flask.request.args.get("container")
    if cmd_str in ("start", "stop", "pause", "unpause", "restart", "kill"): # security :)
        completed_command = subprocessRun(f"docker {cmd_str} {container_name}")
        if completed_command.returncode == 0:
            return flask.make_response("", 204)
        return flask.make_response(completed_command.stdout.decode()+completed_command.stderr.decode(), 500)
    return flask.make_response("Invalid Command", 400)


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
            finally:
                break

    app.run(port=port)