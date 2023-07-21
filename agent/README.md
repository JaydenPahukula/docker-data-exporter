# Docker Data Agent

## Overview

This agent runs in the background and is responsible for providing data on the Docker instance running on the server when requested by the aggregator. Install it on any server that you wish to collect Docker data on (including the aggregator). The agent functions as an API with one endpoint, `get-data`. This will return a JSON object with the all the available data. This agent is open on port 5050 by default after installation.

_Note: The agent can run even if Docker is not installed or running, but it won't return much useful information._

## Installation

To install, just run the following command:
``` bash
bash <(curl -s https://raw.githubusercontent.com/JaydenPahukula/docker-data-exporter/main/agent/scripts/install.sh)
```
This will download the agent and all it's dependencies, then install docker-dash-agent as a systemd service listening on port 5050, which can then be managed using systemctl. For example, you can use the following command to restart the agent:
``` bash
systemctl restart docker-dash-agent.service
```
Or to check the status of the agent
``` bash
systemctl status docker-dash-agent.service
```

</br>

# API Documentation

## Usage

To get data from the agent, send a GET request to the following endpoint:
```
http://placeholder.url/get-data
```

This API will also respond to a request to the base URL with a `200 OK` as a sanity check.

## Example Responses

### Standard
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
      "cpu-percent": 0.00,
      "mem-percent": 0.00,
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
      "cpu-percent": 0.02,
      "mem-percent": 0.19,
      "network-bytes-in": 1126,
      "network-bytes-out": 0,
      "block-bytes-in": 16986931,
      "block-bytes-out": 0
    }
  ]
}
```

### Docker not running
``` JSON
{
  "hostname": "localhost.server4",
  "docker-running": false
}
```