"""
InfraHardening API
Backend API for customer management and infrastructure orchestration
"""

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import Optional, List
import uuid
import os
from datetime import datetime, date
import psycopg2
from psycopg2.extras import RealDictCursor
import json
import subprocess
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="InfraHardening API",
    description="Customer Management and Infrastructure Orchestration API",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Database connection
def get_db_connection():
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        database=os.getenv("DB_NAME", "infrahardening"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", "password"),
        cursor_factory=RealDictCursor
    )
    return conn

# Pydantic models
class CustomerCreate(BaseModel):
    tenant_id: str
    company_name: str
    contact_name: str
    email: EmailStr
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    country: str = "Poland"
    vat_number: Optional[str] = None
    plan_tier: str = "basic"

class CustomerUpdate(BaseModel):
    company_name: Optional[str] = None
    contact_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    vat_number: Optional[str] = None
    status: Optional[str] = None

class SubscriptionCreate(BaseModel):
    customer_id: uuid.UUID
    plan_id: int
    subscription_type: str = "monthly"
    azure_subscription_id: Optional[str] = None
    azure_tenant_id: Optional[str] = None
    azure_client_id: Optional[str] = None

class InfrastructureCreate(BaseModel):
    customer_id: uuid.UUID
    tenant_id: str
    location: str = "West Europe"
    vm_count: int = 1
    vm_size: str = "Standard_B2s"
    plan_tier: str = "basic"

class InvoiceCreate(BaseModel):
    customer_id: uuid.UUID
    subscription_id: uuid.UUID
    amount: float
    due_date: date
    currency: str = "PLN"

# Authentication dependency
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    # Validate token here (implement proper JWT validation)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    return token

# Customer endpoints
@app.post("/api/customers", response_model=dict)
async def create_customer(customer: CustomerCreate, current_user: str = Depends(get_current_user)):
    """Create a new customer"""
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO customers (tenant_id, company_name, contact_name, email, phone, address, city, country, vat_number)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id, tenant_id, company_name, contact_name, email, status, created_at
            """, (
                customer.tenant_id, customer.company_name, customer.contact_name,
                customer.email, customer.phone, customer.address, customer.city,
                customer.country, customer.vat_number
            ))
            result = cur.fetchone()
            conn.commit()
            
            # Create default subscription
            cur.execute("""
                INSERT INTO subscriptions (customer_id, plan_id, subscription_type, start_date)
                SELECT %s, id, %s, CURRENT_DATE
                FROM subscription_plans WHERE tier = %s
                RETURNING id
            """, (result['id'], 'monthly', customer.plan_tier))
            conn.commit()
            
            return {
                "success": True,
                "customer": result,
                "message": "Customer created successfully"
            }
    except Exception as e:
        conn.rollback()
        logger.error(f"Error creating customer: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@app.get("/api/customers", response_model=List[dict])
async def get_customers(current_user: str = Depends(get_current_user)):
    """Get all customers"""
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT c.*, s.plan_id, s.status as subscription_status, 
                       sp.name as plan_name, sp.monthly_price
                FROM customers c
                LEFT JOIN subscriptions s ON c.id = s.customer_id AND s.status = 'active'
                LEFT JOIN subscription_plans sp ON s.plan_id = sp.id
                ORDER BY c.created_at DESC
            """)
            return cur.fetchall()
    except Exception as e:
        logger.error(f"Error getting customers: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@app.get("/api/customers/{customer_id}", response_model=dict)
async def get_customer(customer_id: uuid.UUID, current_user: str = Depends(get_current_user)):
    """Get customer by ID"""
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT c.*, s.plan_id, s.status as subscription_status, 
                       sp.name as plan_name, sp.monthly_price, sp.max_vms
                FROM customers c
                LEFT JOIN subscriptions s ON c.id = s.customer_id AND s.status = 'active'
                LEFT JOIN subscription_plans sp ON s.plan_id = sp.id
                WHERE c.id = %s
            """, (str(customer_id),))
            result = cur.fetchone()
            if not result:
                raise HTTPException(status_code=404, detail="Customer not found")
            return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting customer: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@app.put("/api/customers/{customer_id}", response_model=dict)
async def update_customer(customer_id: uuid.UUID, customer: CustomerUpdate, current_user: str = Depends(get_current_user)):
    """Update customer"""
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            # Build dynamic update query
            update_fields = []
            values = []
            
            for field, value in customer.dict(exclude_unset=True).items():
                update_fields.append(f"{field} = %s")
                values.append(value)
            
            if not update_fields:
                raise HTTPException(status_code=400, detail="No fields to update")
            
            values.append(str(customer_id))
            
            cur.execute(f"""
                UPDATE customers 
                SET {', '.join(update_fields)}, updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
                RETURNING id, tenant_id, company_name, contact_name, email, status
            """, values)
            
            result = cur.fetchone()
            conn.commit()
            
            return {
                "success": True,
                "customer": result,
                "message": "Customer updated successfully"
            }
    except Exception as e:
        conn.rollback()
        logger.error(f"Error updating customer: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

# Subscription endpoints
@app.get("/api/plans", response_model=List[dict])
async def get_plans(current_user: str = Depends(get_current_user)):
    """Get all subscription plans"""
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM subscription_plans WHERE is_active = true ORDER BY monthly_price")
            return cur.fetchall()
    except Exception as e:
        logger.error(f"Error getting plans: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@app.post("/api/subscriptions", response_model=dict)
async def create_subscription(subscription: SubscriptionCreate, current_user: str = Depends(get_current_user)):
    """Create a new subscription"""
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO subscriptions (customer_id, plan_id, subscription_type, start_date, 
                                         azure_subscription_id, azure_tenant_id, azure_client_id)
                VALUES (%s, %s, %s, CURRENT_DATE, %s, %s, %s)
                RETURNING id, customer_id, plan_id, subscription_type, status, start_date
            """, (
                str(subscription.customer_id), subscription.plan_id, subscription.subscription_type,
                subscription.azure_subscription_id, subscription.azure_tenant_id, subscription.azure_client_id
            ))
            result = cur.fetchone()
            conn.commit()
            
            return {
                "success": True,
                "subscription": result,
                "message": "Subscription created successfully"
            }
    except Exception as e:
        conn.rollback()
        logger.error(f"Error creating subscription: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

# Infrastructure endpoints
@app.post("/api/infrastructure/provision", response_model=dict)
async def provision_infrastructure(infra: InfrastructureCreate, current_user: str = Depends(get_current_user)):
    """Provision infrastructure for a customer"""
    try:
        # Generate Terraform configuration
        tenant_tfvars = f"""
tenant_id = "{infra.tenant_id}"
tenant_name = "{infra.tenant_id}"
location = "{infra.location}"
vm_count = {infra.vm_count}
vm_size = "{infra.vm_size}"
plan_tier = "{infra.plan_tier}"
admin_username = "azureuser"
ssh_public_key = "{os.getenv('SSH_PUBLIC_KEY', '')}"
allowed_ssh_cidr = "0.0.0.0/0"
"""
        
        # Write terraform.tfvars
        tfvars_path = f"/tmp/{infra.tenant_id}-terraform.tfvars"
        with open(tfvars_path, 'w') as f:
            f.write(tenant_tfvars)
        
        # Run Terraform (simplified - in production use proper orchestration)
        terraform_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'terraform')
        
        # Initialize
        subprocess.run(['terraform', 'init'], cwd=terraform_dir, check=True)
        
        # Apply
        subprocess.run([
            'terraform', 'apply',
            '-var-file', tfvars_path,
            '-auto-approve'
        ], cwd=terraform_dir, check=True)
        
        # Get outputs
        result = subprocess.run(
            ['terraform', 'output', '-json'],
            cwd=terraform_dir,
            capture_output=True,
            text=True,
            check=True
        )
        
        outputs = json.loads(result.stdout)
        
        # Store in database
        conn = get_db_connection()
        try:
            with conn.cursor() as cur:
                for vm_name in outputs.get('vm_names', []):
                    cur.execute("""
                        INSERT INTO infrastructure_resources 
                        (customer_id, resource_type, resource_id, resource_name, resource_group, location, tier)
                        VALUES (%s, 'vm', %s, %s, %s, %s, %s)
                    """, (
                        str(infra.customer_id), vm_name, vm_name, 
                        outputs.get('resource_group_name'), infra.location, infra.plan_tier
                    ))
                conn.commit()
        finally:
            conn.close()
        
        return {
            "success": True,
            "infrastructure": outputs,
            "message": "Infrastructure provisioned successfully"
        }
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Terraform error: {e}")
        raise HTTPException(status_code=500, detail=f"Infrastructure provisioning failed: {str(e)}")
    except Exception as e:
        logger.error(f"Error provisioning infrastructure: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/infrastructure/{customer_id}", response_model=List[dict])
async def get_infrastructure(customer_id: uuid.UUID, current_user: str = Depends(get_current_user)):
    """Get infrastructure for a customer"""
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT * FROM infrastructure_resources 
                WHERE customer_id = %s 
                ORDER BY created_at DESC
            """, (str(customer_id),))
            return cur.fetchall()
    except Exception as e:
        logger.error(f"Error getting infrastructure: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

# Billing endpoints
@app.get("/api/invoices/{customer_id}", response_model=List[dict])
async def get_invoices(customer_id: uuid.UUID, current_user: str = Depends(get_current_user)):
    """Get invoices for a customer"""
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT i.*, c.company_name 
                FROM invoices i
                JOIN customers c ON i.customer_id = c.id
                WHERE i.customer_id = %s
                ORDER BY i.created_at DESC
            """, (str(customer_id),))
            return cur.fetchall()
    except Exception as e:
        logger.error(f"Error getting invoices: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@app.post("/api/invoices", response_model=dict)
async def create_invoice(invoice: InvoiceCreate, current_user: str = Depends(get_current_user)):
    """Create a new invoice"""
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            invoice_number = f"INV-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"
            
            cur.execute("""
                INSERT INTO invoices (customer_id, subscription_id, invoice_number, amount, currency, due_date)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id, invoice_number, amount, status, due_date
            """, (
                str(invoice.customer_id), str(invoice.subscription_id), invoice_number,
                invoice.amount, invoice.currency, invoice.due_date
            ))
            result = cur.fetchone()
            conn.commit()
            
            return {
                "success": True,
                "invoice": result,
                "message": "Invoice created successfully"
            }
    except Exception as e:
        conn.rollback()
        logger.error(f"Error creating invoice: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
