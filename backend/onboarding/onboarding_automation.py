"""
Customer Onboarding Automation
Automates the entire customer onboarding process
"""

import os
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional
import psycopg2
from psycopg2.extras import RealDictCursor
import subprocess
import json
import yaml

logger = logging.getLogger(__name__)


class OnboardingAutomation:
    """Automates customer onboarding process"""
    
    def __init__(self):
        self.db_host = os.getenv('DB_HOST', 'localhost')
        self.db_name = os.getenv('DB_NAME', 'infrahardening')
        self.db_user = os.getenv('DB_USER', 'postgres')
        self.db_password = os.getenv('DB_PASSWORD', 'password')
        self.terraform_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'terraform')
        self.ansible_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'ansible')
    
    def get_db_connection(self):
        """Get database connection"""
        conn = psycopg2.connect(
            host=self.db_host,
            database=self.db_name,
            user=self.db_user,
            password=self.db_password,
            cursor_factory=RealDictCursor
        )
        return conn
    
    def start_onboarding(self, customer_data: Dict) -> Dict:
        """Start the onboarding process for a new customer"""
        try:
            # Step 1: Create customer in database
            customer_id = self._create_customer(customer_data)
            
            # Step 2: Create subscription
            subscription_id = self._create_subscription(customer_id, customer_data)
            
            # Step 3: Generate unique tenant ID
            tenant_id = self._generate_tenant_id(customer_data['company_name'])
            
            # Step 4: Provision infrastructure
            infra_result = self._provision_infrastructure(
                tenant_id, customer_data['plan_tier'], customer_data
            )
            
            # Step 5: Configure infrastructure with Ansible
            ansible_result = self._configure_infrastructure(
                tenant_id, infra_result
            )
            
            # Step 6: Deploy monitoring agent
            agent_result = self._deploy_monitoring_agent(
                tenant_id, infra_result
            )
            
            # Step 7: Create initial user access
            access_result = self._create_user_access(
                customer_id, customer_data
            )
            
            # Step 8: Send welcome email
            self._send_welcome_email(customer_data, infra_result)
            
            # Step 9: Schedule initial reports
            self._schedule_initial_reports(customer_id)
            
            # Step 10: Update onboarding status
            self._update_onboarding_status(customer_id, 'completed')
            
            return {
                'success': True,
                'customer_id': customer_id,
                'subscription_id': subscription_id,
                'tenant_id': tenant_id,
                'infrastructure': infra_result,
                'message': 'Customer onboarding completed successfully'
            }
            
        except Exception as e:
            logger.error(f"Error during onboarding: {e}")
            # Rollback on failure
            if 'customer_id' in locals():
                self._rollback_onboarding(customer_id)
            raise
    
    def _create_customer(self, customer_data: Dict) -> str:
        """Create customer in database"""
        try:
            conn = self.get_db_connection()
            
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO customers (tenant_id, company_name, contact_name, email, phone, 
                                        address, city, country, vat_number, status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'trial')
                    RETURNING id
                """, (
                    customer_data['tenant_id'],
                    customer_data['company_name'],
                    customer_data['contact_name'],
                    customer_data['email'],
                    customer_data.get('phone'),
                    customer_data.get('address'),
                    customer_data.get('city'),
                    customer_data.get('country', 'Poland'),
                    customer_data.get('vat_number')
                ))
                customer_id = cur.fetchone()['id']
                conn.commit()
                
                logger.info(f"Created customer {customer_id}")
                return customer_id
                
        except Exception as e:
            logger.error(f"Error creating customer: {e}")
            raise
        finally:
            conn.close()
    
    def _create_subscription(self, customer_id: str, customer_data: Dict) -> str:
        """Create subscription for customer"""
        try:
            conn = self.get_db_connection()
            
            with conn.cursor() as cur:
                # Get plan ID
                cur.execute("""
                    SELECT id FROM subscription_plans WHERE tier = %s
                """, (customer_data['plan_tier'],))
                plan = cur.fetchone()
                
                if not plan:
                    raise ValueError(f"Plan tier {customer_data['plan_tier']} not found")
                
                # Create subscription
                cur.execute("""
                    INSERT INTO subscriptions (customer_id, plan_id, subscription_type, start_date)
                    VALUES (%s, %s, 'trial', CURRENT_DATE)
                    RETURNING id
                """, (customer_id, plan['id']))
                subscription_id = cur.fetchone()['id']
                conn.commit()
                
                logger.info(f"Created subscription {subscription_id} for customer {customer_id}")
                return subscription_id
                
        except Exception as e:
            logger.error(f"Error creating subscription: {e}")
            raise
        finally:
            conn.close()
    
    def _generate_tenant_id(self, company_name: str) -> str:
        """Generate unique tenant ID from company name"""
        # Convert to lowercase, remove spaces, add random suffix
        import random
        import string
        
        base_name = company_name.lower().replace(' ', '-').replace('_', '-')
        # Remove special characters
        base_name = ''.join(c for c in base_name if c.isalnum() or c == '-')
        
        # Add random suffix for uniqueness
        suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
        
        return f"{base_name}-{suffix}"
    
    def _provision_infrastructure(self, tenant_id: str, plan_tier: str, 
                                 customer_data: Dict) -> Dict:
        """Provision infrastructure using Terraform"""
        try:
            # Load pricing config to get VM count based on plan
            with open('backend/config/pricing.yaml', 'r') as f:
                pricing_config = yaml.safe_load(f)
            
            plan_config = pricing_config['plans'][plan_tier]
            vm_count = plan_config['limits']['max_vms']
            
            # Generate Terraform variables
            tfvars_content = f"""
tenant_id = "{tenant_id}"
tenant_name = "{tenant_id}"
location = "{customer_data.get('location', 'West Europe')}"
vm_count = {vm_count}
vm_size = "{customer_data.get('vm_size', 'Standard_B2s')}"
plan_tier = "{plan_tier}"
admin_username = "azureuser"
ssh_public_key = "{os.getenv('SSH_PUBLIC_KEY', '')}"
allowed_ssh_cidr = "{customer_data.get('allowed_ssh_cidr', '0.0.0.0/0')}"
"""
            
            # Write terraform.tfvars
            tfvars_path = f"/tmp/{tenant_id}-terraform.tfvars"
            with open(tfvars_path, 'w') as f:
                f.write(tfvars_content)
            
            # Run Terraform
            terraform_module_dir = os.path.join(self.terraform_dir, 'modules', 'tenant')
            
            # Initialize
            subprocess.run(['terraform', 'init'], cwd=terraform_module_dir, check=True)
            
            # Apply
            subprocess.run([
                'terraform', 'apply',
                '-var-file', tfvars_path,
                '-auto-approve'
            ], cwd=terraform_module_dir, check=True)
            
            # Get outputs
            result = subprocess.run(
                ['terraform', 'output', '-json'],
                cwd=terraform_module_dir,
                capture_output=True,
                text=True,
                check=True
            )
            
            outputs = json.loads(result.stdout)
            
            logger.info(f"Provisioned infrastructure for tenant {tenant_id}")
            return outputs
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Terraform error: {e}")
            raise
        except Exception as e:
            logger.error(f"Error provisioning infrastructure: {e}")
            raise
    
    def _configure_infrastructure(self, tenant_id: str, infra_result: Dict) -> Dict:
        """Configure infrastructure with Ansible"""
        try:
            # Generate Ansible inventory from Terraform outputs
            inventory_content = self._generate_ansible_inventory(infra_result)
            
            inventory_path = f"/tmp/{tenant_id}-inventory.ini"
            with open(inventory_path, 'w') as f:
                f.write(inventory_content)
            
            # Run Ansible playbook
            subprocess.run([
                'ansible-playbook',
                '-i', inventory_path,
                'site.yml'
            ], cwd=self.ansible_dir, check=True)
            
            logger.info(f"Configured infrastructure for tenant {tenant_id}")
            return {'success': True}
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Ansible error: {e}")
            raise
        except Exception as e:
            logger.error(f"Error configuring infrastructure: {e}")
            raise
    
    def _generate_ansible_inventory(self, infra_result: Dict) -> str:
        """Generate Ansible inventory from Terraform outputs"""
        inventory = "[webservers]\n"
        
        vm_names = infra_result.get('vm_names', [])
        vm_private_ips = infra_result.get('vm_private_ips', [])
        bastion_ip = infra_result.get('bastion_public_ip')
        
        for i, (vm_name, private_ip) in enumerate(zip(vm_names, vm_private_ips)):
            if i == 0 and bastion_ip:
                inventory += f"{vm_name} ansible_host={bastion_ip} ansible_user=azureuser\n"
            else:
                inventory += f"{vm_name} ansible_host={private_ip} ansible_user=azureuser ansible_ssh_common_args='-o ProxyJump=azureuser@{bastion_ip}'\n"
        
        inventory += "\n[all:vars]\n"
        inventory += "ansible_python_interpreter=/usr/bin/python3\n"
        inventory += "admin_user=azureuser\n"
        
        return inventory
    
    def _deploy_monitoring_agent(self, tenant_id: str, infra_result: Dict) -> Dict:
        """Deploy Go monitoring agent to infrastructure"""
        try:
            # Build agent
            go_agent_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'go-agent')
            subprocess.run(['go', 'build', '-o', 'agent', 'main.go'], cwd=go_agent_dir, check=True)
            
            # Deploy to all VMs
            vm_names = infra_result.get('vm_names', [])
            bastion_ip = infra_result.get('bastion_public_ip')
            
            for vm_name in vm_names:
                # Copy agent binary
                subprocess.run([
                    'ansible', vm_name,
                    '-i', f"/tmp/{tenant_id}-inventory.ini",
                    '-m', 'copy',
                    '-a', f"src={go_agent_dir}/agent dest=/usr/local/bin/agent mode=0755"
                ], cwd=self.ansible_dir, check=True)
                
                # Copy systemd service
                subprocess.run([
                    'ansible', vm_name,
                    '-i', f"/tmp/{tenant_id}-inventory.ini",
                    '-m', 'copy',
                    '-a', f"src={go_agent_dir}/systemd/agent.service dest=/etc/systemd/system/agent.service"
                ], cwd=self.ansible_dir, check=True)
                
                # Start service
                subprocess.run([
                    'ansible', vm_name,
                    '-i', f"/tmp/{tenant_id}-inventory.ini",
                    '-m', 'systemd',
                    '-a', "name=agent daemon_reload=yes enabled=yes state=started"
                ], cwd=self.ansible_dir, check=True)
            
            logger.info(f"Deployed monitoring agent for tenant {tenant_id}")
            return {'success': True}
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Error deploying monitoring agent: {e}")
            raise
        except Exception as e:
            logger.error(f"Error deploying monitoring agent: {e}")
            raise
    
    def _create_user_access(self, customer_id: str, customer_data: Dict) -> Dict:
        """Create user access credentials"""
        try:
            conn = self.get_db_connection()
            
            with conn.cursor() as cur:
                # Generate API key for customer
                import secrets
                api_key = secrets.token_urlsafe(32)
                
                cur.execute("""
                    INSERT INTO api_keys (customer_id, name, key_hash, scopes)
                    VALUES (%s, 'Default API Key', %s, ARRAY['read', 'write'])
                    RETURNING id
                """, (customer_id, api_key))
                api_key_id = cur.fetchone()['id']
                conn.commit()
                
                logger.info(f"Created user access for customer {customer_id}")
                return {
                    'api_key_id': api_key_id,
                    'api_key': api_key  # Return only once, then store securely
                }
                
        except Exception as e:
            logger.error(f"Error creating user access: {e}")
            raise
        finally:
            conn.close()
    
    def _send_welcome_email(self, customer_data: Dict, infra_result: Dict):
        """Send welcome email to customer"""
        try:
            # In production, integrate with email service (SendGrid, AWS SES, etc.)
            logger.info(f"Welcome email would be sent to {customer_data['email']}")
            
            # Placeholder for email content
            email_content = f"""
            Welcome to InfraHardening!
            
            Your infrastructure has been provisioned successfully.
            
            Tenant ID: {infra_result.get('tenant_id')}
            Bastion IP: {infra_result.get('bastion_public_ip')}
            
            You can access your dashboard at: https://dashboard.infrahardening.com
            """
            
            logger.info(f"Email content: {email_content}")
            
        except Exception as e:
            logger.error(f"Error sending welcome email: {e}")
            # Non-critical, don't raise
    
    def _schedule_initial_reports(self, customer_id: str):
        """Schedule initial reports for new customer"""
        try:
            conn = self.get_db_connection()
            
            with conn.cursor() as cur:
                # Schedule security report for tomorrow
                tomorrow = datetime.now() + timedelta(days=1)
                
                cur.execute("""
                    INSERT INTO reports (customer_id, report_type, period_start, period_end, status)
                    VALUES (%s, 'security', CURRENT_DATE, %s::date, 'scheduled')
                """, (customer_id, tomorrow))
                
                conn.commit()
                
                logger.info(f"Scheduled initial reports for customer {customer_id}")
                
        except Exception as e:
            logger.error(f"Error scheduling initial reports: {e}")
            # Non-critical, don't raise
        finally:
            conn.close()
    
    def _update_onboarding_status(self, customer_id: str, status: str):
        """Update onboarding status in database"""
        try:
            conn = self.get_db_connection()
            
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE customers 
                    SET status = %s, trial_end_date = CURRENT_DATE + INTERVAL '14 days'
                    WHERE id = %s
                """, ('active' if status == 'completed' else 'pending', customer_id))
                conn.commit()
                
                logger.info(f"Updated onboarding status for customer {customer_id} to {status}")
                
        except Exception as e:
            logger.error(f"Error updating onboarding status: {e}")
            raise
        finally:
            conn.close()
    
    def _rollback_onboarding(self, customer_id: str):
        """Rollback onboarding process on failure"""
        try:
            logger.warning(f"Rolling back onboarding for customer {customer_id}")
            
            # In production, implement proper rollback:
            # 1. Destroy Terraform infrastructure
            # 2. Delete from database
            # 3. Cancel any subscriptions
            
            conn = self.get_db_connection()
            
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE customers SET status = 'failed' WHERE id = %s
                """, (customer_id,))
                conn.commit()
                
        except Exception as e:
            logger.error(f"Error during rollback: {e}")
        finally:
            conn.close()


# Webhook handler for onboarding triggers
class OnboardingWebhook:
    """Handles webhooks that trigger onboarding"""
    
    def __init__(self):
        self.automation = OnboardingAutomation()
    
    def handle_payment_webhook(self, webhook_data: Dict) -> Dict:
        """Handle payment success webhook to trigger onboarding"""
        try:
            if webhook_data.get('event') == 'payment_success':
                customer_email = webhook_data.get('customer_email')
                plan_tier = webhook_data.get('plan_tier')
                
                # Get customer data from pending registration
                customer_data = self._get_pending_customer(customer_email)
                
                if customer_data:
                    # Start onboarding
                    result = self.automation.start_onboarding(customer_data)
                    return {
                        'success': True,
                        'message': 'Onboarding started successfully',
                        'customer_id': result['customer_id']
                    }
                else:
                    return {
                        'success': False,
                        'message': 'No pending customer found'
                    }
            
        except Exception as e:
            logger.error(f"Error handling payment webhook: {e}")
            return {'success': False, 'error': str(e)}
    
    def _get_pending_customer(self, email: str) -> Optional[Dict]:
        """Get pending customer data"""
        # In production, implement proper pending customer storage
        return {
            'tenant_id': 'pending',
            'company_name': 'Test Company',
            'contact_name': 'Test Contact',
            'email': email,
            'plan_tier': 'basic',
            'location': 'West Europe'
        }


if __name__ == '__main__':
    # Example usage
    onboarding = OnboardingAutomation()
    
    customer_data = {
        'tenant_id': 'test-company',
        'company_name': 'Test Company',
        'contact_name': 'John Doe',
        'email': 'john@test.com',
        'phone': '+48 123 456 789',
        'address': 'Test Address',
        'city': 'Warsaw',
        'country': 'Poland',
        'vat_number': 'PL1234567890',
        'plan_tier': 'basic',
        'location': 'West Europe'
    }
    
    result = onboarding.start_onboarding(customer_data)
    print(f"Onboarding result: {result}")
