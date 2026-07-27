terraform {
  required_version = ">= 1.0"
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
  }
}

variable "tenant_id" {
  description = "Unique identifier for the tenant/customer"
  type        = string
}

variable "tenant_name" {
  description = "Name of the tenant/customer"
  type        = string
}

variable "location" {
  description = "Azure region for tenant resources"
  type        = string
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
}

locals {
  prefix = "${var.tenant_id}-${var.plan_tier}"
  rg_name = var.resource_group_name != "" ? var.resource_group_name : "${local.prefix}-rg"
}

# Resource Group
resource "azurerm_resource_group" "tenant" {
  name     = local.rg_name
  location = var.location

  tags = merge(var.tags, {
    TenantID      = var.tenant_id
    TenantName    = var.tenant_name
    PlanTier      = var.plan_tier
    ManagedBy     = "InfraHardening"
    Environment   = "production"
  })
}

# Virtual Network
resource "azurerm_virtual_network" "tenant" {
  name                = "${local.prefix}-vnet"
  address_space       = ["10.${substr(var.tenant_id, -2, 2)}.0.0/16"]
  location            = azurerm_resource_group.tenant.location
  resource_group_name = azurerm_resource_group.tenant.name

  tags = var.tags
}

# Subnets based on plan tier
resource "azurerm_subnet" "web" {
  count                = var.vm_count > 0 ? 1 : 0
  name                 = "web-subnet"
  resource_group_name  = azurerm_resource_group.tenant.name
  virtual_network_name = azurerm_virtual_network.tenant.name
  address_prefixes     = ["10.${substr(var.tenant_id, -2, 2)}.1.0/24"]
}

resource "azurerm_subnet" "app" {
  count                = var.vm_count > 1 ? 1 : 0
  name                 = "app-subnet"
  resource_group_name  = azurerm_resource_group.tenant.name
  virtual_network_name = azurerm_virtual_network.tenant.name
  address_prefixes     = ["10.${substr(var.tenant_id, -2, 2)}.2.0/24"]
}

resource "azurerm_subnet" "db" {
  count                = var.plan_tier == "enterprise" ? 1 : 0
  name                 = "db-subnet"
  resource_group_name  = azurerm_resource_group.tenant.name
  virtual_network_name = azurerm_virtual_network.tenant.name
  address_prefixes     = ["10.${substr(var.tenant_id, -2, 2)}.3.0/24"]
}

# Network Security Group
resource "azurerm_network_security_group" "tenant" {
  name                = "${local.prefix}-nsg"
  location            = azurerm_resource_group.tenant.location
  resource_group_name = azurerm_resource_group.tenant.name

  dynamic "security_rule" {
    for_each = var.plan_tier == "basic" ? [1] : []
    content {
      name                       = "SSH"
      priority                   = 100
      direction                  = "Inbound"
      access                     = "Allow"
      protocol                   = "Tcp"
      source_port_range          = "*"
      destination_port_range     = "22"
      source_address_prefix      = var.allowed_ssh_cidr
      destination_address_prefix = "*"
    }
  }

  dynamic "security_rule" {
    for_each = var.plan_tier != "basic" ? [1] : []
    content {
      name                       = "SSH"
      priority                   = 100
      direction                  = "Inbound"
      access                     = "Allow"
      protocol                   = "Tcp"
      source_port_range          = "*"
      destination_port_range     = "22"
      source_address_prefix      = var.allowed_ssh_cidr
      destination_address_prefix = "*"
    }
    content {
      name                       = "HTTP"
      priority                   = 110
      direction                  = "Inbound"
      access                     = "Allow"
      protocol                   = "Tcp"
      source_port_range          = "*"
      destination_port_range     = "80"
      source_address_prefix      = "*"
      destination_address_prefix = "*"
    }
    content {
      name                       = "HTTPS"
      priority                   = 120
      direction                  = "Inbound"
      access                     = "Allow"
      protocol                   = "Tcp"
      source_port_range          = "*"
      destination_port_range     = "443"
      source_address_prefix      = "*"
      destination_address_prefix = "*"
    }
  }

  security_rule {
    name                       = "DenyAllInbound"
    priority                   = 4096
    direction                  = "Inbound"
    access                     = "Deny"
    protocol                   = "*"
    source_port_range          = "*"
    destination_port_range     = "*"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }

  tags = var.tags
}

# Associate NSG with subnets
resource "azurerm_subnet_network_security_group_association" "web" {
  count = var.vm_count > 0 ? 1 : 0

  subnet_id                 = azurerm_subnet.web[0].id
  network_security_group_id = azurerm_network_security_group.tenant.id
}

resource "azurerm_subnet_network_security_group_association" "app" {
  count = var.vm_count > 1 ? 1 : 0

  subnet_id                 = azurerm_subnet.app[0].id
  network_security_group_id = azurerm_network_security_group.tenant.id
}

resource "azurerm_subnet_network_security_group_association" "db" {
  count = var.plan_tier == "enterprise" ? 1 : 0

  subnet_id                 = azurerm_subnet.db[0].id
  network_security_group_id = azurerm_network_security_group.tenant.id
}

# Public IP (only for bastion in basic/pro plans)
resource "azurerm_public_ip" "bastion" {
  count = var.plan_tier != "enterprise" ? 1 : 0

  name                = "${local.prefix}-bastion-pip"
  location            = azurerm_resource_group.tenant.location
  resource_group_name = azurerm_resource_group.tenant.name
  allocation_method   = "Static"
  sku                 = "Standard"

  tags = var.tags
}

# Network Interfaces
resource "azurerm_network_interface" "bastion" {
  count = var.plan_tier != "enterprise" ? 1 : 0

  name                = "${local.prefix}-bastion-nic"
  location            = azurerm_resource_group.tenant.location
  resource_group_name = azurerm_resource_group.tenant.name

  ip_configuration {
    name                          = "internal"
    subnet_id                     = azurerm_subnet.web[0].id
    private_ip_address_allocation = "Dynamic"
    public_ip_address_id          = azurerm_public_ip.bastion[0].id
  }

  tags = var.tags
}

resource "azurerm_network_interface" "worker" {
  count = var.vm_count > 1 ? var.vm_count - 1 : 0

  name                = "${local.prefix}-worker-${count.index}-nic"
  location            = azurerm_resource_group.tenant.location
  resource_group_name = azurerm_resource_group.tenant.name

  ip_configuration {
    name                          = "internal"
    subnet_id                     = var.plan_tier == "enterprise" ? azurerm_subnet.db[0].id : azurerm_subnet.app[0].id
    private_ip_address_allocation = "Dynamic"
  }

  tags = var.tags
}

# SSH Key
resource "azurerm_ssh_public_key" "tenant" {
  name                = "${local.prefix}-ssh-key"
  resource_group_name = azurerm_resource_group.tenant.name
  location            = azurerm_resource_group.tenant.location
  public_key          = var.ssh_public_key
}

# Linux Virtual Machines
resource "azurerm_linux_virtual_machine" "bastion" {
  count = var.plan_tier != "enterprise" ? 1 : 0

  name                  = "${local.prefix}-bastion"
  location              = azurerm_resource_group.tenant.location
  resource_group_name   = azurerm_resource_group.tenant.name
  size                  = var.vm_size
  admin_username        = var.admin_username
  network_interface_ids = [azurerm_network_interface.bastion[0].id]

  admin_ssh_key {
    username   = var.admin_username
    public_key = azurerm_ssh_public_key.tenant.public_key
  }

  os_disk {
    name                 = "${local.prefix}-bastion-osdisk"
    caching              = "ReadWrite"
    storage_account_type = var.plan_tier == "enterprise" ? "Premium_LRS" : "Standard_LRS"
  }

  source_image_reference {
    publisher = "almalinux"
    offer     = "almalinux-hpc"
    sku       = "8_8"
    version   = "latest"
  }

  tags = merge(var.tags, {
    Role = "bastion"
  })
}

resource "azurerm_linux_virtual_machine" "worker" {
  count = var.vm_count > 1 ? var.vm_count - 1 : 0

  name                  = "${local.prefix}-worker-${count.index}"
  location              = azurerm_resource_group.tenant.location
  resource_group_name   = azurerm_resource_group.tenant.name
  size                  = var.vm_size
  admin_username        = var.admin_username
  network_interface_ids = [azurerm_network_interface.worker[count.index].id]

  admin_ssh_key {
    username   = var.admin_username
    public_key = azurerm_ssh_public_key.tenant.public_key
  }

  os_disk {
    name                 = "${local.prefix}-worker-${count.index}-osdisk"
    caching              = "ReadWrite"
    storage_account_type = var.plan_tier == "enterprise" ? "Premium_LRS" : "Standard_LRS"
  }

  source_image_reference {
    publisher = "almalinux"
    offer     = "almalinux-hpc"
    sku       = "8_8"
    version   = "latest"
  }

  tags = merge(var.tags, {
    Role = "worker"
  })
}

# Outputs
output "resource_group_name" {
  value = azurerm_resource_group.tenant.name
}

output "virtual_network_id" {
  value = azurerm_virtual_network.tenant.id
}

output "bastion_public_ip" {
  value = var.plan_tier != "enterprise" ? azurerm_public_ip.bastion[0].ip_address : null
}

output "vm_names" {
  value = compact(concat(
    var.plan_tier != "enterprise" ? [azurerm_linux_virtual_machine.bastion[0].name] : [],
    azurerm_linux_virtual_machine.worker[*].name
  ))
}

output "vm_private_ips" {
  value = compact(concat(
    var.plan_tier != "enterprise" ? [azurerm_network_interface.bastion[0].private_ip_address] : [],
    azurerm_network_interface.worker[*].private_ip_address
  ))
}

output "tenant_id" {
  value = var.tenant_id
}

output "plan_tier" {
  value = var.plan_tier
}
