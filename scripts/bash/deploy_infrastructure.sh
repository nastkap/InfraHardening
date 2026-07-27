#!/bin/bash
#
# Infrastructure Deployment Script
# Orchestrates the deployment of Azure infrastructure using Terraform
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
TERRAFORM_DIR="$PROJECT_ROOT/terraform"
ANSIBLE_DIR="$PROJECT_ROOT/ansible"

# Functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_dependencies() {
    log_info "Checking dependencies..."
    
    local deps=("terraform" "ansible" "az" "jq")
    for dep in "${deps[@]}"; do
        if ! command -v "$dep" &> /dev/null; then
            log_error "$dep is not installed"
            return 1
        fi
    done
    
    log_info "All dependencies are installed"
}

check_azure_auth() {
    log_info "Checking Azure authentication..."
    
    if az account show &> /dev/null; then
        log_info "Azure authentication successful"
        az account show
    else
        log_error "Azure authentication failed. Run 'az login'"
        return 1
    fi
}

terraform_init() {
    log_info "Initializing Terraform..."
    cd "$TERRAFORM_DIR"
    terraform init
}

terraform_plan() {
    log_info "Running Terraform plan..."
    cd "$TERRAFORM_DIR"
    terraform plan -out=tfplan
}

terraform_apply() {
    log_info "Applying Terraform configuration..."
    cd "$TERRAFORM_DIR"
    terraform apply tfplan
}

terraform_destroy() {
    log_warn "Destroying Terraform infrastructure..."
    cd "$TERRAFORM_DIR"
    terraform destroy -auto-approve
}

generate_ansible_inventory() {
    log_info "Generating Ansible inventory from Terraform outputs..."
    cd "$TERRAFORM_DIR"
    
    # Get Terraform outputs
    local vm_names=$(terraform output -json vm_names | jq -r '.[]')
    local vm_public_ips=$(terraform output -json vm_public_ips | jq -r '.[]')
    local vm_private_ips=$(terraform output -json vm_private_ips | jq -r '.[]')
    
    # Generate inventory file
    cat > "$ANSIBLE_DIR/inventory/hosts.ini" << EOF
[webservers]
EOF
    
    local i=0
    for vm_name in $vm_names; do
        local public_ip=$(echo "$vm_public_ips" | sed -n "$((i+1))p")
        local private_ip=$(echo "$vm_private_ips" | sed -n "$((i+1))p")
        
        if [ "$i" -eq 0 ]; then
            echo "$vm_name ansible_host=$public_ip ansible_user=azureuser" >> "$ANSIBLE_DIR/inventory/hosts.ini"
        else
            echo "$vm_name ansible_host=$private_ip ansible_user=azureuser ansible_ssh_common_args='-o ProxyJump=azureuser@$public_ip'" >> "$ANSIBLE_DIR/inventory/hosts.ini"
        fi
        ((i++))
    done
    
    cat >> "$ANSIBLE_DIR/inventory/hosts.ini" << EOF

[all:vars]
ansible_python_interpreter=/usr/bin/python3
admin_user=azureuser
EOF
    
    log_info "Ansible inventory generated"
}

run_ansible_playbook() {
    log_info "Running Ansible playbook..."
    cd "$ANSIBLE_DIR"
    ansible-playbook -i inventory/hosts.ini site.yml
}

wait_for_ssh() {
    local host=$1
    local max_attempts=30
    local attempt=1
    
    log_info "Waiting for SSH to be available on $host..."
    
    while [ $attempt -le $max_attempts ]; do
        if ssh -o ConnectTimeout=5 -o StrictHostKeyChecking=no azureuser@$host "echo 'SSH is ready'" &> /dev/null; then
            log_info "SSH is ready on $host"
            return 0
        fi
        log_info "Attempt $attempt/$max_attempts: SSH not ready yet..."
        sleep 10
        ((attempt++))
    done
    
    log_error "SSH did not become available on $host"
    return 1
}

deploy() {
    log_info "Starting infrastructure deployment..."
    
    check_dependencies
    check_azure_auth
    terraform_init
    terraform_plan
    terraform_apply
    
    # Get bastion host IP
    local bastion_ip=$(cd "$TERRAFORM_DIR" && terraform output -raw public_ip_address)
    
    wait_for_ssh "$bastion_ip"
    generate_ansible_inventory
    run_ansible_playbook
    
    log_info "Deployment completed successfully"
}

destroy() {
    log_warn "Starting infrastructure destruction..."
    
    check_dependencies
    check_azure_auth
    terraform_destroy
    
    log_info "Destruction completed"
}

# Main script
case "${1:-deploy}" in
    deploy)
        deploy
        ;;
    destroy)
        destroy
        ;;
    plan)
        check_dependencies
        check_azure_auth
        terraform_init
        terraform_plan
        ;;
    ansible)
        generate_ansible_inventory
        run_ansible_playbook
        ;;
    *)
        echo "Usage: $0 {deploy|destroy|plan|ansible}"
        exit 1
        ;;
esac
