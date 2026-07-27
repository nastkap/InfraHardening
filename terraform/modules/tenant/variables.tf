variable "tenant_id" {
  description = "Unique identifier for the tenant/customer"
  type        = string
  validation {
    condition     = can(regex("^[a-z0-9-]{3,20}$", var.tenant_id))
    error_message = "Tenant ID must be 3-20 characters, lowercase letters, numbers, and hyphens only."
  }
}

variable "tenant_name" {
  description = "Name of the tenant/customer"
  type        = string
}

variable "location" {
  description = "Azure region for tenant resources"
  type        = string
  default     = "West Europe"
}

variable "resource_group_name" {
  description = "Resource group name for tenant"
  type        = string
  default     = ""
}

variable "vm_count" {
  description = "Number of VMs for this tenant"
  type        = number
  default     = 1
  validation {
    condition     = var.vm_count >= 1 && var.vm_count <= 50
    error_message = "VM count must be between 1 and 50."
  }
}

variable "vm_size" {
  description = "Size of VMs"
  type        = string
  default     = "Standard_B2s"
}

variable "admin_username" {
  description = "Admin username"
  type        = string
  default     = "azureuser"
}

variable "ssh_public_key" {
  description = "SSH public key"
  type        = string
}

variable "allowed_ssh_cidr" {
  description = "Allowed SSH CIDR"
  type        = string
  default     = "0.0.0.0/0"
}

variable "tags" {
  description = "Additional tags"
  type        = map(string)
  default     = {}
}

variable "plan_tier" {
  description = "Plan tier (basic, pro, enterprise)"
  type        = string
  default     = "basic"
  validation {
    condition     = contains(["basic", "pro", "enterprise"], var.plan_tier)
    error_message = "Plan tier must be one of: basic, pro, enterprise."
  }
}
