# Docker Data Aggregator

## Overview

The aggregator is the middle man between Prometheus and the individual agents. Only one server should be the aggregator for each cluster of servers to manage. The aggregator runs as an API, which waits for the Prometheus query, then scrapes all IP addresses in its list. It returns all datapoints in [Prometheus's text-based data format](#https://prometheus.io/docs/instrumenting/exposition_formats/), which get written to the database.

## Prometheus Configuration

Coming soon...

## Installation

Coming soon...
