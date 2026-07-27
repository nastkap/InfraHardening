# Architecture Documentation

## Overview

The Cloud Infrastructure Hardening & Compliance Pipeline implements a comprehensive security-hardened infrastructure deployment system for Azure using Infrastructure as Code (IaC), Configuration Management, and GitOps principles.

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        CI/CD Pipeline                            │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐     │
│  │ GitHub Actions│───▶│   Jenkins    │───▶│   Terraform  │     │
│  └──────────────┘    └──────────────┘    └──────────────┘     │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Azure Infrastructure                         │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Virtual Network (10.0.0.0/16)                            │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐      │  │
│  │  │ Web Subnet  │  │ App Subnet  │  │ DB Subnet   │      │  │
│  │  │ 10.0.1.0/24 │  │ 10.0.2.0/24 │  │ 10.0.3.0/24 │      │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘      │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Network Security Group                                   │  │
│  │  - SSH (22) from allowed CIDR                            │  │
│  │  - HTTP (80) from any                                     │  │
│  │  - HTTPS (443) from any                                   │  │
│  │  - Deny all other inbound traffic                        │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Virtual Machines (AlmaLinux/Ubuntu)                       │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐      │  │
│  │  │ Bastion Host│  │ Worker VM 1 │  │ Worker VM 2 │      │  │
│  │  │ (Public IP) │  │ (Private IP)│  │ (Private IP)│      │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘      │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Configuration Management                      │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐     │
│  │   Ansible    │───▶│ System       │───▶│ Hardened     │     │
│  │   Playbooks  │    │ Hardening    │    │ Servers      │     │
│  └──────────────┘    └──────────────┘    └──────────────┘     │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Monitoring & Diagnostics                      │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐     │
│  │  Go Agent    │───▶│ Prometheus   │───▶│  Grafana     │     │
│  │  (systemd)   │    │  Metrics     │    │  Dashboards  │     │
│  └──────────────┘    └──────────────┘    └──────────────┘     │
└─────────────────────────────────────────────────────────────────┘
```

## Components

### 1. Infrastructure Provisioning (Terraform)

**Purpose**: Automate Azure resource creation and management

**Components**:
- Virtual Network (VNet) with isolated subnets
- Network Security Groups (NSG) with strict firewall rules
- Linux Virtual Machines (AlmaLinux/Ubuntu)
- Public IP addresses for bastion host
- SSH key management

**Security Features**:
- Network isolation through subnets
- NSG rules limiting SSH access
- SSH key-based authentication only
- No public IPs for worker VMs (except bastion)

### 2. Configuration Management (Ansible)

**Purpose**: Automate system hardening and configuration

**Roles**:
- **system-update**: Package updates and essential software installation
- **ssh-hardening**: SSH security hardening (disable password auth, root login)
- **firewall-configuration**: Firewall setup (firewalld/ufw)
- **user-management**: Admin user creation and sudo configuration
- **security-hardening**: System security hardening (sysctl, fail2ban, auditd)
- **monitoring-setup**: Prometheus Node Exporter installation

**Security Features**:
- SSH key-only authentication
- Disabled root login
- Configured firewall rules
- Fail2ban for brute-force protection
- Audit logging enabled
- System hardening via sysctl

### 3. Diagnostics Agent (Go)

**Purpose**: Real-time system monitoring and diagnostics

**Features**:
- CPU, memory, disk usage monitoring
- Network connection tracking
- Port availability checking
- Network route tracing
- Prometheus metrics endpoint
- HTTP API for diagnostics
- Systemd service integration

**Endpoints**:
- `GET /health` - Health check
- `GET /metrics` - Prometheus metrics
- `GET /diagnostics` - Full system diagnostics

### 4. Orchestration Scripts

**Python Scripts**:
- Azure REST API integration
- Infrastructure inventory export
- VM status monitoring
- Network configuration retrieval

**Bash Scripts**:
- Infrastructure deployment orchestration
- Health check automation
- Ansible inventory generation

### 5. CI/CD Pipeline

**GitHub Actions**:
- YAML/JSON validation
- Security scanning (tfsec, gosec, bandit)
- Linting (ansible-lint, pylint)
- Automated testing
- Deployment automation

**Jenkins**:
- Declarative pipeline (Jenkinsfile)
- Terraform plan/apply
- Ansible playbook execution
- Manual approval gates
- Artifact management

### 6. Monitoring Stack

**Prometheus**:
- Metrics collection from Go agents
- Time-series database
- Alerting capabilities

**Grafana**:
- Dashboard visualization
- Real-time metrics display
- Network connectivity monitoring
- Infrastructure overview

## Security Architecture

### Network Security
1. **Network Isolation**: Separate subnets for web, app, and database tiers
2. **NSG Rules**: Strict inbound/outbound traffic filtering
3. **Bastion Pattern**: Single entry point with public IP
4. **Private Communication**: Worker VMs use private IPs only

### System Security
1. **SSH Hardening**: Key-based authentication only
2. **Firewall**: Configured firewalld/ufw with minimal open ports
3. **Fail2ban**: Brute-force attack protection
4. **Audit Logging**: System audit daemon enabled
5. **System Hardening**: Kernel parameter hardening via sysctl

### Operational Security
1. **IaC**: Infrastructure defined as code, version-controlled
2. **GitOps**: Declarative configuration via Git
3. **Automated Testing**: Security scanning in CI/CD
4. **Monitoring**: Real-time security metrics
5. **Audit Trail**: Comprehensive logging

## Data Flow

1. **Deployment Flow**:
   ```
   Code Push → GitHub Actions → Jenkins → Terraform Apply → 
   Ansible Playbooks → Go Agent Deployment → Monitoring
   ```

2. **Monitoring Flow**:
   ```
   Go Agent → Prometheus Metrics → Grafana Dashboard → Alerts
   ```

3. **Diagnostics Flow**:
   ```
   Go Agent → HTTP API → Python Scripts → Azure REST API → Inventory
   ```

## Scalability Considerations

- **Horizontal Scaling**: Add more VMs via Terraform variable
- **Multi-Environment**: Support for dev/staging/prod environments
- **Modular Design**: Each component can be scaled independently
- **GitOps Ready**: Easy to extend with additional tools

## Disaster Recovery

- **State Management**: Terraform state stored in Azure Storage
- **Configuration Versioning**: All configuration in Git
- **Automated Backups**: Can be extended with backup automation
- **Infrastructure as Code**: Easy to recreate from scratch
