# Docker Data Aggregator

## Overview

The aggregator is the middle man between Prometheus and the individual agents. Only one server should be the aggregator for each cluster of servers to manage. The aggregator runs as an API, which waits for the Prometheus query, then scrapes all IP addresses in its list. It returns all datapoints in [Prometheus's text-based data format](#https://prometheus.io/docs/instrumenting/exposition_formats/), which get written to the database.

## Prometheus Configuration

Coming soon...

## Installation

Coming soon...

</br>

# API Documentation:

The aggregator has two endpoints, [metrics] and [add-agent]. This API will also respond to a request to the base URL with a `200 OK` as a sanity check.

## Metrics

This is the endpoint that is called by Prometheus when it wants to scrape data. The aggregator will scrape all IP addresses in its list and format the data to give to Prometheus.

### Usage:

```
<GET> http://placeholder.url/metrics
```

### Example Response:
See [Prometheus text-based exposition format](#https://prometheus.io/docs/instrumenting/exposition_formats/).

```
server_ip{hostname="localhost.server1",server_ip="127.0.0.1:5050"} 1
server_hostname{hostname="localhost.server1",server_hostname="localhost.server1"} 1
server_agent_running{hostname="localhost.server1"} 1
server_docker_running{hostname="localhost.server1"} 1
server_docker_version{hostname="localhost.server1",server_docker_version="24.0.4 (build 3713ee1)"} 1
server_swarm_mode{hostname="localhost.server1"} 0
server_image_count{hostname="localhost.server1"} 3
server_total_container_count{hostname="localhost.server1"} 2
server_running_container_count{hostname="localhost.server1"} 0
```

## Add Agent

This endpoint adds the caller's IP to the aggregator's IP list, found in `aggregator_config.yaml`. You can still easily add and remove IPs manually, this endpoint just makes it simpler to set up each agent.

### Usage:

```
<POST> http://placeholder.url/add-agent?port=[PORT]
```
The 'port' arguement is optional, and if omitted, the aggregator will store the ip with no specific port, although this is almost always called with `port=5050` because that is the default port of the agent.

### Example Response:

```
Successfully added agent 127.0.0.1:5050
```