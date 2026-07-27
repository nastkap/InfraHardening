# Infrastructure Hardening Agent

A lightweight Go-based diagnostic and monitoring agent for Linux servers.

## Features

- System diagnostics (CPU, memory, disk, network)
- Port availability checking
- Network route tracing
- Prometheus metrics endpoint
- HTTP API for diagnostics
- Systemd service integration

## Building

```bash
go build -o agent main.go
```

## Installation

```bash
sudo cp agent /usr/local/bin/
sudo cp systemd/agent.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable agent
sudo systemctl start agent
```

## Usage

The agent exposes the following endpoints:

- `GET /health` - Health check
- `GET /metrics` - Prometheus metrics
- `GET /diagnostics` - Full system diagnostics

## Configuration

Environment variables:

- `AGENT_PORT` - HTTP server port (default: 8080)
- `AGENT_CHECK_INTERVAL` - Check interval in seconds (default: 30)
