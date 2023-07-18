from datetime import datetime
import flask
import json
import sys

from methods.subprocess_run import subprocessRun

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

    output["swarm-state"] = docker_info["Swarm"]["LocalNodeState"]
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
            "user": status["Names"].split("--")[-1],
            "state": status["State"],
            "status": status["Status"]
        }

        created_at = datetime.strptime(status["CreatedAt"], "%Y-%m-%d %H:%M:%S %z %Z")
        container_output["created-at"] = created_at.timestamp()

        completed_command = subprocessRun("docker stats --no-stream --format json " + status["ID"])
        container_stats = json.loads(completed_command.stdout.decode())
        
        network_in, network_out = (x[:-1] for x in container_stats["NetIO"].split(" / "))
        block_in, block_out = (x[:-1] for x in container_stats["BlockIO"].split(" / "))
        
        container_output.update({
            "cpu_percent": container_stats["CPUPerc"][:-1],
            "mem_percent": container_stats["MemPerc"][:-1],
            "network-bytes-in": network_in,
            "network-bytes-out": network_out,
            "block-bytes-in": block_in,
            "block-bytes-out": block_out
        })

        completed_command = subprocessRun("docker stats --no-stream --format json " + status["ID"])
        container_stats = json.loads(completed_command.stdout.decode())

        output["containers"].append(container_output)


    return flask.make_response(json.dumps(output), 200)



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