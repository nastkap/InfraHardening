# Grafana Dashboards

This directory contains Grafana dashboard configurations for monitoring the infrastructure.

## Dashboards

### Infrastructure Overview
- **File**: `infrastructure-overview.json`
- **UID**: `infra-overview`
- **Metrics**:
  - CPU usage (gauge)
  - Memory usage (gauge)
  - Disk usage (gauge)
  - Network connections (stat)
  - CPU usage over time (timeseries)
  - Memory usage over time (timeseries)
  - Port status (stat)

### Network Connectivity
- **File**: `network-connectivity.json`
- **UID**: `network-connectivity`
- **Metrics**:
  - Total network connections
  - Average connections per host
  - Network connections over time
  - TCP port status

## Datasources

### Prometheus
- **File**: `datasources/prometheus.yml`
- **URL**: `http://prometheus:9090`

## Installation

### Using Grafana API

```bash
# Import Infrastructure Overview dashboard
curl -X POST \
  -H "Content-Type: application/json" \
  -d @dashboards/infrastructure-overview.json \
  http://admin:admin@localhost:3000/api/dashboards/db

# Import Network Connectivity dashboard
curl -X POST \
  -H "Content-Type: application/json" \
  -d @dashboards/network-connectivity.json \
  http://admin:admin@localhost:3000/api/dashboards/db
```

### Using Grafana UI

1. Navigate to Dashboards → Import
2. Upload the JSON files from the `dashboards` directory
3. Configure the datasource to point to your Prometheus instance

## Configuration

The dashboards expect the following Prometheus metrics from the Go agent:

- `agent_cpu_usage_percent` - CPU usage percentage
- `agent_memory_usage_percent` - Memory usage percentage
- `agent_disk_usage_percent` - Disk usage percentage
- `agent_network_connections` - Number of network connections
- `agent_port_check_result` - Port check results (1 = open, 0 = closed)

## Refresh Rate

Dashboards are configured to refresh every 10 seconds by default. This can be adjusted in the dashboard JSON configuration.
