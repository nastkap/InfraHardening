output "resource_group_name" {
  description = "Name of the resource group"
  value       = azurerm_resource_group.main.name
}

output "virtual_network_id" {
  description = "ID of the virtual network"
  value       = azurerm_virtual_network.main.id
}

output "virtual_network_name" {
  description = "Name of the virtual network"
  value       = azurerm_virtual_network.main.name
}

output "subnet_ids" {
  description = "IDs of the subnets"
  value = {
    web = azurerm_subnet.web.id
    app = azurerm_subnet.app.id
    db  = azurerm_subnet.db.id
  }
}

output "public_ip_address" {
  description = "Public IP address of the bastion host"
  value       = azurerm_public_ip.main.ip_address
}

output "vm_private_ips" {
  description = "Private IP addresses of the VMs"
  value = azurerm_network_interface.main[*].private_ip_address
}

output "vm_public_ips" {
  description = "Public IP addresses of the VMs"
  value = azurerm_linux_virtual_machine.main[*].public_ip_address
}

output "vm_names" {
  description = "Names of the VMs"
  value       = azurerm_linux_virtual_machine.main[*].name
}

output "network_security_group_id" {
  description = "ID of the network security group"
  value       = azurerm_network_security_group.main.id
}

output "location" {
  description = "Location of the resources"
  value       = azurerm_resource_group.main.location
}
