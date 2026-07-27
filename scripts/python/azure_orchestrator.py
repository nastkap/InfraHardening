#!/usr/bin/env python3
"""
Azure Infrastructure Orchestrator
Communicates with Azure REST API to manage infrastructure
"""

import os
import json
import requests
import argparse
from datetime import datetime
from typing import Dict, List, Optional


class AzureOrchestrator:
    """Orchestrator for Azure REST API operations"""
    
    def __init__(self, subscription_id: str, tenant_id: str, client_id: str, client_secret: str):
        self.subscription_id = subscription_id
        self.tenant_id = tenant_id
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = None
        self.base_url = f"https://management.azure.com/subscriptions/{subscription_id}"
        
    def authenticate(self) -> bool:
        """Authenticate with Azure AD and get access token"""
        auth_url = f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token"
        
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'scope': 'https://management.azure.com/.default',
            'grant_type': 'client_credentials'
        }
        
        try:
            response = requests.post(auth_url, data=data)
            response.raise_for_status()
            self.access_token = response.json()['access_token']
            return True
        except requests.exceptions.RequestException as e:
            print(f"Authentication failed: {e}")
            return False
    
    def get_headers(self) -> Dict[str, str]:
        """Get headers with authentication token"""
        return {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
    
    def get_virtual_machines(self, resource_group: str) -> List[Dict]:
        """Get all virtual machines in a resource group"""
        url = f"{self.base_url}/resourceGroups/{resource_group}/providers/Microsoft.Compute/virtualMachines?api-version=2023-03-01"
        
        try:
            response = requests.get(url, headers=self.get_headers())
            response.raise_for_status()
            return response.json().get('value', [])
        except requests.exceptions.RequestException as e:
            print(f"Failed to get VMs: {e}")
            return []
    
    def get_vm_details(self, resource_group: str, vm_name: str) -> Optional[Dict]:
        """Get detailed information about a specific VM"""
        url = f"{self.base_url}/resourceGroups/{resource_group}/providers/Microsoft.Compute/virtualMachines/{vm_name}?api-version=2023-03-01"
        
        try:
            response = requests.get(url, headers=self.get_headers())
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Failed to get VM details: {e}")
            return None
    
    def get_vm_network_interfaces(self, resource_group: str, vm_name: str) -> List[Dict]:
        """Get network interfaces for a VM"""
        vm_details = self.get_vm_details(resource_group, vm_name)
        if not vm_details:
            return []
        
        nics = []
        for nic_ref in vm_details.get('properties', {}).get('networkProfile', {}).get('networkInterfaces', []):
            nic_id = nic_ref['id']
            nic_name = nic_id.split('/')[-1]
            nics.append({'id': nic_id, 'name': nic_name})
        
        return nics
    
    def get_public_ip_addresses(self, resource_group: str) -> List[Dict]:
        """Get all public IP addresses in a resource group"""
        url = f"{self.base_url}/resourceGroups/{resource_group}/providers/Microsoft.Network/publicIPAddresses?api-version=2023-02-01"
        
        try:
            response = requests.get(url, headers=self.get_headers())
            response.raise_for_status()
            return response.json().get('value', [])
        except requests.exceptions.RequestException as e:
            print(f"Failed to get public IPs: {e}")
            return []
    
    def get_network_security_groups(self, resource_group: str) -> List[Dict]:
        """Get all network security groups in a resource group"""
        url = f"{self.base_url}/resourceGroups/{resource_group}/providers/Microsoft.Network/networkSecurityGroups?api-version=2023-02-01"
        
        try:
            response = requests.get(url, headers=self.get_headers())
            response.raise_for_status()
            return response.json().get('value', [])
        except requests.exceptions.RequestException as e:
            print(f"Failed to get NSGs: {e}")
            return []
    
    def get_virtual_networks(self, resource_group: str) -> List[Dict]:
        """Get all virtual networks in a resource group"""
        url = f"{self.base_url}/resourceGroups/{resource_group}/providers/Microsoft.Network/virtualNetworks?api-version=2023-02-01"
        
        try:
            response = requests.get(url, headers=self.get_headers())
            response.raise_for_status()
            return response.json().get('value', [])
        except requests.exceptions.RequestException as e:
            print(f"Failed to get VNets: {e}")
            return []
    
    def export_inventory(self, resource_group: str, output_file: str, format: str = 'yaml'):
        """Export infrastructure inventory to file"""
        vms = self.get_virtual_machines(resource_group)
        public_ips = self.get_public_ip_addresses(resource_group)
        
        inventory = {
            'timestamp': datetime.utcnow().isoformat(),
            'resource_group': resource_group,
            'virtual_machines': [],
            'public_ips': []
        }
        
        for vm in vms:
            vm_name = vm['name']
            vm_info = {
                'name': vm_name,
                'location': vm['location'],
                'type': vm['type'],
                'tags': vm.get('tags', {}),
                'status': 'running'  # Simplified status
            }
            inventory['virtual_machines'].append(vm_info)
        
        for ip in public_ips:
            ip_info = {
                'name': ip['name'],
                'ip_address': ip.get('properties', {}).get('ipAddress'),
                'allocation_method': ip.get('properties', {}).get('publicIPAllocationMethod'),
                'tags': ip.get('tags', {})
            }
            inventory['public_ips'].append(ip_info)
        
        if format == 'json':
            with open(output_file, 'w') as f:
                json.dump(inventory, f, indent=2)
        elif format == 'yaml':
            import yaml
            with open(output_file, 'w') as f:
                yaml.dump(inventory, f, default_flow_style=False)
        
        print(f"Inventory exported to {output_file}")
        return inventory


def main():
    parser = argparse.ArgumentParser(description='Azure Infrastructure Orchestrator')
    parser.add_argument('--subscription-id', required=True, help='Azure Subscription ID')
    parser.add_argument('--tenant-id', required=True, help='Azure Tenant ID')
    parser.add_argument('--client-id', required=True, help='Azure Client ID')
    parser.add_argument('--client-secret', required=True, help='Azure Client Secret')
    parser.add_argument('--resource-group', required=True, help='Resource Group name')
    parser.add_argument('--action', choices=['list-vms', 'get-vm', 'export-inventory'], 
                        default='list-vms', help='Action to perform')
    parser.add_argument('--vm-name', help='VM name (for get-vm action)')
    parser.add_argument('--output-file', help='Output file path (for export-inventory)')
    parser.add_argument('--format', choices=['json', 'yaml'], default='yaml',
                        help='Output format (for export-inventory)')
    
    args = parser.parse_args()
    
    orchestrator = AzureOrchestrator(
        args.subscription_id,
        args.tenant_id,
        args.client_id,
        args.client_secret
    )
    
    if not orchestrator.authenticate():
        print("Authentication failed")
        return 1
    
    if args.action == 'list-vms':
        vms = orchestrator.get_virtual_machines(args.resource_group)
        print(f"Found {len(vms)} VMs in resource group {args.resource_group}")
        for vm in vms:
            print(f"  - {vm['name']} ({vm['location']})")
    
    elif args.action == 'get-vm':
        if not args.vm_name:
            print("VM name required for get-vm action")
            return 1
        vm_details = orchestrator.get_vm_details(args.resource_group, args.vm_name)
        print(json.dumps(vm_details, indent=2))
    
    elif args.action == 'export-inventory':
        if not args.output_file:
            print("Output file required for export-inventory action")
            return 1
        orchestrator.export_inventory(args.resource_group, args.output_file, args.format)
    
    return 0


if __name__ == '__main__':
    exit(main())
