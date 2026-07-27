#!/bin/bash
#
# Health Check Script
# Checks the health of deployed infrastructure components
#

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
TERRAFORM_DIR="$PROJECT_ROOT/terraform"

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_vm_status() {
    log_info "Checking VM status..."
    
    cd "$TERRAFORM_DIR"
    local vm_names=$(terraform output -json vm_names | jq -r '.[]')
    
    for vm_name in $vm_names; do
        log_info "Checking $vm_name..."
        # This would typically use Azure CLI to check VM status
        az vm show --name "$vm_name" --resource-group infra-hardening-rg --show-details || true
    done
}

check_network_connectivity() {
    log_info "Checking network connectivity..."
    
    cd "$TERRAFORM_DIR"
    local bastion_ip=$(terraform output -raw public_ip_address)
    
    if ssh -o ConnectTimeout=5 -o StrictHostKeyChecking=no azureuser@$bastion_ip "echo 'SSH connectivity OK'" &> /dev/null; then
        log_info "SSH connectivity to bastion host: OK"
    else
        log_error "SSH connectivity to bastion host: FAILED"
        return 1
    fi
}

check_agent_status() {
    log_info "Checking agent status..."
    
    cd "$TERRAFORM_DIR"
    local bastion_ip=$(terraform output -raw public_ip_address)
    
    local health_check=$(ssh -o ConnectTimeout=5 -o StrictHostKeyChecking=no azureuser@$bastion_ip "curl -s http://localhost:8080/health" || echo "failed")
    
    if echo "$health_check" | grep -q "healthy"; then
        log_info "Agent health check: OK"
    else
        log_warn "Agent health check: FAILED or not installed"
    fi
}

check_prometheus_metrics() {
    log_info "Checking Prometheus metrics..."
    
    cd "$TERRAFORM_DIR"
    local bastion_ip=$(terraform output -raw public_ip_address)
    
    local metrics=$(ssh -o ConnectTimeout=5 -o StrictHostKeyChecking=no azureuser@$bastion_ip "curl -s http://localhost:8080/metrics" || echo "failed")
    
    if echo "$metrics" | grep -q "agent_cpu_usage"; then
        log_info "Prometheus metrics: OK"
    else
        log_warn "Prometheus metrics: FAILED or not available"
    fi
}

main() {
    log_info "Starting health checks..."
    
    check_vm_status
    check_network_connectivity
    check_agent_status
    check_prometheus_metrics
    
    log_info "Health checks completed"
}

main "$@"
