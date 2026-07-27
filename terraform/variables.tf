variable "resource_group_name" {
  description = "Name of the resource group"
  type        = string
  default     = "infra-hardening-rg"
}

variable "location" {
  description = "Azure region for resources"
  type        = string
  default     = "West Europe"
}

variable "prefix" {
  description = "Prefix for resource names"
  type        = string
  default     = "infrahard"
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "prod"
}

variable "vm_count" {
  description = "Number of virtual machines to create"
  type        = number
  default     = 3
}

variable "vm_size" {
  description = "Size of the virtual machines"
  type        = string
  default     = "Standard_B2s"
}

variable "admin_username" {
  description = "Admin username for VMs"
  type        = string
  default     = "azureuser"
}

variable "ssh_public_key_path" {
  description = "Path to SSH public key"
  type        = string
  default     = "~/.ssh/id_rsa.pub"
}

variable "allowed_ssh_cidr" {
  description = "CIDR block allowed for SSH access"
  type        = string
  default     = "0.0.0.0/0"
}

variable "vm_image_publisher" {
  description = "VM image publisher"
  type        = string
  default     = "almalinux"
}

variable "vm_image_offer" {
  description = "VM image offer"
  type        = string
  default     = "almalinux-hpc"
}

variable "vm_image_sku" {
  description = "VM image SKU"
  type        = string
  default     = "8_8"
}

variable "boot_diagnostics_storage_account" {
  description = "Storage account URI for boot diagnostics"
  type        = string
  default     = ""
}
