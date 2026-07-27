# GitHub Actions Workflows

This directory contains GitHub Actions workflows for CI/CD and security scanning.

## Workflows

### CI Pipeline (ci.yml)

Triggered on:
- Push to `main` or `develop` branches
- Pull requests to `main` branch

Jobs:
1. **Validate Terraform** - Formats, validates, and security scans Terraform configuration
2. **Validate Ansible** - Lints and syntax checks Ansible playbooks
3. **Build Go Agent** - Compiles and tests the Go monitoring agent
4. **Lint Python** - Runs pylint and bandit on Python scripts
5. **Validate YAML** - Validates YAML files with yamllint
6. **Security Scan** - Runs Trivy vulnerability scanner

### Deploy Infrastructure (deploy.yml)

Triggered on:
- Push to `main` branch
- Manual workflow dispatch

Jobs:
1. **Deploy to Azure** - Full infrastructure deployment including:
   - Terraform apply
   - Ansible playbook execution
   - Go agent deployment
   - Health checks

## Required Secrets

Configure the following secrets in your GitHub repository:

### Azure Secrets
- `AZURE_CREDENTIALS` - Azure service principal credentials (JSON format)
- `TF_STATE_RG` - Terraform state resource group name
- `TF_STATE_SA` - Terraform state storage account name

### Other Secrets
- `TF_API_TOKEN` - Terraform Cloud API token (if using Terraform Cloud)
- `SLACK_WEBHOOK` - Slack webhook for deployment notifications

## Usage

Workflows run automatically on push/PR. Manual deployment can be triggered via the Actions tab in GitHub.
