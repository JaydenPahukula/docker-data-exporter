# Docker Data Aggregator

## Overview

The aggregator is the middle man between Prometheus and the individual agents. Only one server should be the aggregator for each cluster of servers to manage. The aggregator runs as an API, which waits for the Prometheus query, then scrapes all IP addresses in its list. It returns all datapoints in [Prometheus's text-based data format](#https://prometheus.io/docs/instrumenting/exposition_formats/), which get written to the database.


## Installation

First, download the code with wget using this command:
```
curl -sSLo ./repo.tar https://api.github.com/repos/JaydenPahukula/docker-data-exporter/tarball
```
Next, extract the tar archive and remove the .tar file:
```
tar -xf repo.tar && rm repo.tar
```
This will put the repository into a directory called something like 'JaydenPahukula-docker-data-exporter', and you can rename it if you want. Move into the repository, then into the 'aggregator' directory. Now you can start the aggregator with:
```
.venv/bin/python main.py
```
This starts the aggregator at localhost port 5000. You can specify a different port with:
```
.venv/bin/python main.py -p [PORT NUMBER]
```
The aggregator will now wait for Prometheus to query it, then it will scrape each IP in its list of known IPs. You can view and change this list in a file called `aggergator_config.yaml`. Also, if you specify this aggregators IP when running the install script on an agent, it will automatically add itself to this list.


## Prometheus Configuration

If not already installed, follow [these](https://prometheus.io/docs/introduction/first_steps/) download steps.

Now navigate into your prometheus folder and open `prometheus.yml`. Under 'scrape_configs', there should be a job called 'prometheus'. If you plan on hosting prometheus on a port besides the default (9090), change the port in 'targets'. You can also change the scrape and evaluation interval at the top in the global settings.

After the 'prometheus' job, add another job by pasting this code: (change the IP and port if necessary)
``` yaml
  - job_name: "docker-data"
    static_configs:
    - targets: ["localhost:5000"]
    metric_relabel_configs:
    - source_labels: [ hostname ]
      separator: ;
      action: replace
      regex: (.*)
      replacement: $1
      target_label: instance
```
This tells prometheus to scrape the aggregator at localhost:5000, and tells it to use the agents' hostname label as the instance, instead of the aggregator. Now you can start the prometheus instance with this command:
```
./prometheus --config.file=prometheus.yml --web.listen-address=:[PORT]
```
You can omit the last option if you are using the default port (9090). Now prometheus is running, and it should periodically hit the aggregator with a query for data. You can check if data is being recorded by going to localhost:9090 (or whatever port you used) in a browser.

Your Prometheus database is now ready to be used in a Grafana dashboard!

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