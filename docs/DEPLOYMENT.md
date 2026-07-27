# Deployment Guide

This guide provides step-by-step instructions for deploying the Cloud Infrastructure Hardening & Compliance Pipeline.

## Prerequisites

### Azure Account
- Active Azure subscription with Owner or Contributor permissions
- Azure Service Principal with appropriate permissions
- Azure CLI installed and configured

### Local Tools
- Terraform >= 1.5.0
- Ansible >= 2.15.0
- Go >= 1.21.0
- Python >= 3.11
- Azure CLI >= 2.50.0
- Git

### SSH Keys
Generate SSH key pair for authentication:
```bash
ssh-keygen -t rsa -b 4096 -f ~/.ssh/azure_infra
```

## Initial Setup

### 1. Clone Repository
```bash
git clone <repository-url>
cd projekt
```

### 2. Configure Azure Authentication

#### Option A: Azure CLI
```bash
az login
az account set --subscription <subscription-id>
```

#### Option B: Service Principal
```bash
export ARM_SUBSCRIPTION_ID="<subscription-id>"
export ARM_CLIENT_ID="<client-id>"
export ARM_CLIENT_SECRET="<client-secret>"
export ARM_TENANT_ID="<tenant-id>"
```

### 3. Create Terraform State Storage
```bash
# Create resource group for state
az group create --name terraform-state-rg --location westeurope

# Create storage account
az storage account create \
  --name terraformstatestorage \
  --resource-group terraform-state-rg \
  --location westeurope \
  --sku Standard_LRS \
  --kind StorageV2

# Create container
az storage container create \
  --name terraform-state \
  --account-name terraformstatestorage
```

### 4. Configure Terraform Variables
```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with your values
```

Update the following variables:
- `resource_group_name`
- `location`
- `vm_count`
- `admin_username`
- `ssh_public_key_path`
- `allowed_ssh_cidr` (set to your IP/32 for SSH access)

## Deployment Steps

### Step 1: Validate Terraform Configuration
```bash
cd terraform
terraform init
terraform fmt -check
terraform validate
```

### Step 2: Review Terraform Plan
```bash
terraform plan -out=tfplan
```

### Step 3: Apply Terraform Configuration
```bash
terraform apply tfplan
```

### Step 4: Generate Ansible Inventory
```bash
cd ../scripts/bash
./deploy_infrastructure.sh ansible
```

### Step 5: Configure Ansible
```bash
cd ../../ansible
# Update inventory/hosts.ini with actual VM IPs from Terraform output
```

### Step 6: Run Ansible Playbook
```bash
ansible-playbook -i inventory/hosts.ini site.yml
```

### Step 7: Build and Deploy Go Agent
```bash
cd ../go-agent
go build -o agent main.go

# Deploy to all VMs
cd ../ansible
ansible all -i inventory/hosts.ini -m copy \
  -a "src=../go-agent/agent dest=/usr/local/bin/agent mode=0755"
ansible all -i inventory/hosts.ini -m copy \
  -a "src=../go-agent/systemd/agent.service dest=/etc/systemd/system/agent.service"
ansible all -i inventory/hosts.ini -m systemd \
  -a "name=agent daemon_reload=yes enabled=yes state=started"
```

### Step 8: Verify Deployment
```bash
cd ../scripts/bash
./health_check.sh
```

### Step 9: Configure Monitoring

#### Install Prometheus
```bash
# On monitoring server
docker run -d \
  --name prometheus \
  -p 9090:9090 \
  -v /path/to/prometheus.yml:/etc/prometheus/prometheus.yml \
  prom/prometheus
```

#### Install Grafana
```bash
# On monitoring server
docker run -d \
  --name grafana \
  -p 3000:3000 \
  grafana/grafana
```

#### Import Dashboards
1. Access Grafana at http://localhost:3000
2. Navigate to Dashboards → Import
3. Upload JSON files from `grafana/dashboards/`
4. Configure Prometheus datasource

## Automated Deployment

### Using Jenkins
1. Configure Jenkins with required credentials
2. Create pipeline job pointing to `jenkins/Jenkinsfile`
3. Run the pipeline

### Using GitHub Actions
1. Configure repository secrets:
   - `AZURE_CREDENTIALS`
   - `TF_STATE_RG`
   - `TF_STATE_SA`
2. Push to main branch to trigger deployment
3. Or manually trigger via Actions tab

## Verification

### Check VM Status
```bash
az vm list --resource-group infra-hardening-rg --show-details
```

### Check Network Connectivity
```bash
# SSH to bastion host
ssh -i ~/.ssh/azure_infra azureuser@<bastion-ip>

# Check agent status
curl http://localhost:8080/health
curl http://localhost:8080/diagnostics
```

### Check Monitoring
- Access Grafana dashboard
- Verify metrics are being collected
- Check for any alerts

## Troubleshooting

### Terraform Issues
```bash
# Reinitialize
terraform init -reconfigure

# Refresh state
terraform refresh

# Import existing resources
terraform import <resource_type>.<name> <resource_id>
```

### Ansible Issues
```bash
# Test connectivity
ansible all -i inventory/hosts.ini -m ping

# Verbose output
ansible-playbook -i inventory/hosts.ini site.yml -vvv

# Check syntax
ansible-playbook -i inventory/hosts.ini site.yml --syntax-check
```

### Go Agent Issues
```bash
# Check logs
sudo journalctl -u agent -f

# Restart service
sudo systemctl restart agent

# Check status
sudo systemctl status agent
```

## Cleanup

### Destroy Infrastructure
```bash
cd terraform
terraform destroy -auto-approve
```

### Remove State Storage
```bash
az storage account delete \
  --name terraformstatestorage \
  --resource-group terraform-state-rg

az group delete --name terraform-state-rg
```

## Security Considerations

1. **SSH Access**: Restrict `allowed_ssh_cidr` to your specific IP
2. **Secrets Management**: Use Azure Key Vault for sensitive data
3. **Network Security**: Review NSG rules regularly
4. **Monitoring**: Set up alerts for suspicious activities
5. **Updates**: Regularly update Terraform providers and Ansible roles
