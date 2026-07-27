# Jenkins Pipeline Configuration

This directory contains the Jenkins pipeline configuration for the Cloud Infrastructure Hardening project.

## Jenkinsfile

The `Jenkinsfile` defines a declarative pipeline that automates the entire infrastructure deployment process:

### Stages

1. **Checkout** - Checks out the source code
2. **Validate Terraform** - Validates Terraform configuration
3. **Terraform Plan** - Generates and reviews the Terraform plan
4. **Security Scan - Terraform** - Runs security scanning with tfsec
5. **Validate Ansible** - Validates Ansible playbooks
6. **Build Go Agent** - Compiles the Go monitoring agent
7. **Security Scan - Go** - Runs security scanning with gosec
8. **Python Linting** - Lints Python scripts with pylint and bandit
9. **Approval - Deploy** - Manual approval for production deployment
10. **Terraform Apply** - Applies the Terraform configuration
11. **Generate Ansible Inventory** - Generates Ansible inventory from Terraform outputs
12. **Run Ansible Playbook** - Executes Ansible hardening playbooks
13. **Deploy Go Agent** - Deploys the Go agent to all VMs
14. **Health Checks** - Runs health checks on deployed infrastructure
15. **Export Inventory** - Exports infrastructure inventory

## Required Jenkins Plugins

- Pipeline
- Terraform
- Ansible
- Go
- Warnings Next Generation (for tfsec, gosec, pylint)
- Credentials Binding
- Email Extension

## Required Credentials

Configure the following credentials in Jenkins:

- `azure-subscription-id` - Azure Subscription ID
- `azure-client-id` - Azure Service Principal Client ID
- `azure-client-secret` - Azure Service Principal Client Secret
- `azure-tenant-id` - Azure Tenant ID

## Environment Variables

The pipeline uses the following environment variables:

- `TERRAFORM_VERSION` - Terraform version to use
- `ANSIBLE_VERSION` - Ansible version to use
- `GO_VERSION` - Go version to use

## Usage

1. Create a new Pipeline job in Jenkins
2. Point it to your Git repository
3. Configure the pipeline script path to `jenkins/Jenkinsfile`
4. Configure the required credentials
5. Run the pipeline
