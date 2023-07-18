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

    # getting container count
    completed_command = subprocessRun("docker ps -a --format {{.Names}}")
    total_container_count = completed_command.stdout.decode().count("\n")
    output["total-container-count"] = total_container_count

    # getting running container count
    completed_command = subprocessRun("docker ps --format {{.Names}}")
    running_container_count = completed_command.stdout.decode().count("\n")
    output["running-container-count"] = running_container_count

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