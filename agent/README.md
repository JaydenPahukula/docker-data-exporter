# Docker Dash Grafana Agent API

## Overview

This agent functions as an API with one endpoint, `get-data`. This will return a JSON object with the all the available data.

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
      "user": "john",
      "state": "exited",
      "status": "Exited (0) About an hour ago",
      "cpu_percent": "0.00",
      "mem_percent": "0.00",
      "network_bytes_in": "0",
      "network_bytes_out": "0",
      "block_bytes_in": "0",
      "block_bytes_out": "0"
    },
    {
      "id": "f08aaca7ab91",
      "name": "httpd--admin",
      "image": "httpd",
      "user": "admin",
      "state": "running",
      "status": "Up About an hour",
      "cpu_percent": "0.03",
      "mem_percent": "0.26",
      "network_bytes_in": "656",
      "network_bytes_out": "0",
      "block_bytes_in": "0",
      "block_bytes_out": "0"
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