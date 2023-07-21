# Docker Data Exporter

Docker Data Exporter is a set of tools for collecting data on Docker containers and storing it in a Prometheus database. It can be installed on many servers at once, and collects data like engine info, container counts, and statuses of each container. The purpose of this project is to be able to use a Grafana Dashboard to monitor server and container statistics.

## Architecture:

_\*insert image here\*_

### Agent:

The agent is installed on any server that you wish to track Docker data on. It is where all the data originates from, and it returns the data upon request. Learn more about the agent and how to install it [here](#https://github.com/JaydenPahukula/docker-data-exporter/blob/main/agent/README.md).

### Aggregator:

The aggregator is the middle man between Prometheus and the individual agents. Prometheus will periodically query the aggregator, then the aggregator scrapes its known list of IP addresses, and collects all the data and gives it to Prometheus.  
The purpose of the aggregator is to manage the agents, so Prometheus only has to scrape one target. If a server is offline, the aggregator can handle it so that Prometheus isn't stuck with empty values, and the user can know that it is down. But beware, the aggregator is a single point of failure, meaning that if it goes down, no data from any server will reach Prometheus. Learn more about the aggregator and how to install it [here](#https://github.com/JaydenPahukula/docker-data-exporter/blob/main/aggregator/README.md).