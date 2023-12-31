# Docker Data Agent

## Overview

This agent runs in the background as a systemd service and is responsible for providing data on the Docker instance running on the server when requested by the aggregator. Install it on any server that you wish to collect Docker data on (including the aggregator). The agent runs as an API that returns a JSON object with the all the available data when the `/get-data` endpoint is queried. It can also run certain docker commands using the `/command` endpoint. This agent is listens on localhost port 5050 by default after installation.

_Note: The agent can run even if Docker is not installed or running, but it won't return useful information._

## Installation

To install, run the following command:

``` bash
bash <(curl -s https://raw.githubusercontent.com/JaydenPahukula/docker-data-exporter/main/agent/scripts/install.sh) [AGGREGATOR_IP*]
```

_*Aggregator ip is optional_  

This will run an install script that downloads the agent and dependencies and automatically configures everything.

If the IP address of the aggregator is provided, it will try to contact and add itself to the aggregator. If it is unsuccessful or no IP is provided, you will have to add it manually. Do this by adding the server's IP address to `server_ips` in `aggregator_config.yaml` on the aggregator machine.

The script will install docker-dash-agent as a systemd service listening on port 5050, which can then be managed using systemctl. For example, you can use the following command to restart the agent:
``` bash
systemctl restart docker-dash-agent.service
```
Or to check the status of the agent
``` bash
systemctl status docker-dash-agent.service
```

</br>

# API Documentation

The agent has two endpoints, [/get-data](#get-data) for scraping data, and [/command](#command) for running docker commands. It will also respond to the base URL with `200 OK`.

## Get Data

### Usage

To get data from the agent, send a GET request to the following endpoint:
```
<GET> http://placeholder.url/get-data
```

### Example Responses

#### Standard:
``` JSON
{
  "hostname": "localhost.server4",
  "docker-running": true,
  "docker-version": "24.0.4 (build 3713ee1)",
  "swarm-mode": false,
  "image-count": 1,
  "total-container-count": 2,
  "running-container-count": 1,
  "containers": [
    {
      "id": "58b587bc20a4",
      "name": "httpd--john",
      "image": "httpd",
      "image-label": "",
      "user": "john",
      "state": "exited",
      "status": "Exited (0) 24 hours ago",
      "created-at": 1689640559,
      "cpu-percent": 0,
      "mem-percent": 0,
      "network-bytes-in": 0,
      "network-bytes-out": 0,
      "block-bytes-in": 0,
      "block-bytes-out": 0
    },
    {
      "id": "f08aaca7ab91",
      "name": "httpd--admin",
      "image": "httpd",
      "image-label": "",
      "user": "admin",
      "state": "running",
      "status": "Up 27 minutes",
      "created-at": 1688777727,
      "cpu-percent": 2,
      "mem-percent": 19,
      "network-bytes-in": 1126,
      "network-bytes-out": 0,
      "block-bytes-in": 16986931,
      "block-bytes-out": 0
    }
  ]
}
```

#### Docker not running:
``` JSON
{
  "hostname": "localhost.server4",
  "docker-running": false
}
```

### Notes about Data Formatting

- To help with formatting for Prometheus, all datatypes will be either a string or an integer
- The `created-at` datapoint is an integer representing the UNIX timestamp of a container's creation
- An empty `image-label` datapoint is the same as "`image:latest`"

## Command

### Usage

To excecute a docker command, run this command:
```
<POST> http://placeholder.url/command/[COMMAND]?container=[CONTAINER_NAME]
```
- `COMMAND_STR` - Docker command to run, for example `.../command/start` executes `docker start`. Must be 'start', 'stop', 'pause', 'unpause', 'restart', or 'kill'
- `CONTAINER_NAME` - Name of container to run the command on

### Response

- If successful, it will return `204` (no content).
- If the command string is not valid, it will return `400 Invalid Command`.
- If the command fails, it will return `500` with stdout and stderr from the docker command.
