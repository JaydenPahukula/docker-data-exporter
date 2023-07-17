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
  "docker-running": true,
  "total-container-count": 1,
  "running-container-count": 0
}
```

### Docker not running
``` JSON
{
  "docker-running": false
}
```