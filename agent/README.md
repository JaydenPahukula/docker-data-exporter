# Docker Dash Grafana Agent

## Overview

This agent functions as an API with one endpoint, `get-data`. This will return a JSON object with the all the available data. This agent functions on port 5050 by default after installation.

## Installation


# API Documentation

## Usage

```
http://placeholder.url/get-data
```

## Example Responses

### Standard
``` JSON
{
  "hostname": "localhost.server4",
  "docker-running": true,
  "docker-version": "24.0.4 (build 3713ee1)",
  "swarm-state": "inactive",
  "image-count": 1,
  "total-container-count": 2,
  "running-container-count": 1,
  "containers": [
    {
      "id": "58b587bc20a4",
      "name": "httpd--john",
      "image": "httpd",
      "image-labels": "",
      "user": "john",
      "state": "exited",
      "status": "Exited (0) About an hour ago",
      "created-at": 1689640559.0,
      "cpu-percent": "0.00",
      "mem-percent": "0.00",
      "network-bytes-in": "0",
      "network-bytes-out": "0",
      "block-bytes-in": "0",
      "block-bytes-out": "0"
    },
    {
      "id": "f08aaca7ab91",
      "name": "httpd--admin",
      "image": "httpd",
      "image-labels": "",
      "user": "admin",
      "state": "running",
      "status": "Up About an hour",
      "created-at": 1688777727.0,
      "cpu-percent": "0.03",
      "mem-percent": "0.26",
      "network-bytes-in": "656",
      "network-bytes-out": "0",
      "block-bytes-in": "0",
      "block-bytes-out": "0"
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