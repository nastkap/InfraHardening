-- Customer Management Database Schema
-- PostgreSQL Schema for Multi-Tenant Infrastructure Management

-- Extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Customers Table
CREATE TABLE customers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id VARCHAR(50) UNIQUE NOT NULL,
    company_name VARCHAR(255) NOT NULL,
    contact_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(50),
    address TEXT,
    city VARCHAR(100),
    country VARCHAR(100) DEFAULT 'Poland',
    vat_number VARCHAR(50),
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'suspended', 'cancelled', 'trial')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    trial_end_date TIMESTAMP WITH TIME ZONE,
    notes TEXT
);

-- Subscription Plans
CREATE TABLE subscription_plans (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    tier VARCHAR(20) unique NOT NULL CHECK (tier IN ('basic', 'pro', 'enterprise')),
    monthly_price DECIMAL(10,2) NOT NULL,
    annual_price DECIMAL(10,2) NOT NULL,
    max_vms INTEGER DEFAULT 3,
    max_users INTEGER DEFAULT 5,
    support_level VARCHAR(20) DEFAULT 'email' CHECK (support_level IN ('email', 'chat', 'phone', '24/7')),
    features JSONB,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Customer Subscriptions
CREATE TABLE subscriptions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_id UUID REFERENCES customers(id) ON DELETE CASCADE,
    plan_id INTEGER REFERENCES subscription_plans(id),
    subscription_type VARCHAR(20) DEFAULT 'monthly' CHECK (subscription_type IN ('monthly', 'annual')),
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'past_due', 'cancelled', 'trial')),
    start_date DATE NOT NULL,
    end_date DATE,
    auto_renew BOOLEAN DEFAULT true,
    azure_subscription_id VARCHAR(100),
    azure_tenant_id VARCHAR(100),
    azure_client_id VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Infrastructure Resources
CREATE TABLE infrastructure_resources (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_id UUID REFERENCES customers(id) ON DELETE CASCADE,
    resource_type VARCHAR(50) NOT NULL CHECK (resource_type IN ('vm', 'vnet', 'nsg', 'storage', 'database')),
    resource_id VARCHAR(255) NOT NULL,
    resource_name VARCHAR(255) NOT NULL,
    resource_group VARCHAR(255),
    location VARCHAR(100),
    status VARCHAR(20) DEFAULT 'running' CHECK (status IN ('running', 'stopped', 'deallocated', 'error')),
    tier VARCHAR(20),
    size VARCHAR(50),
    monthly_cost DECIMAL(10,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB
);

-- Usage Metrics
CREATE TABLE usage_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_id UUID REFERENCES customers(id) ON DELETE CASCADE,
    resource_id UUID REFERENCES infrastructure_resources(id),
    metric_type VARCHAR(50) NOT NULL CHECK (metric_type IN ('cpu', 'memory', 'disk', 'network', 'requests')),
    metric_value DECIMAL(10,2),
    unit VARCHAR(20),
    recorded_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Invoices
CREATE TABLE invoices (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_id UUID REFERENCES customers(id) ON DELETE CASCADE,
    subscription_id UUID REFERENCES subscriptions(id),
    invoice_number VARCHAR(50) UNIQUE NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'PLN',
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'paid', 'overdue', 'cancelled')),
    due_date DATE NOT NULL,
    paid_date DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    pdf_url TEXT
);

-- Invoice Items
CREATE TABLE invoice_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    invoice_id UUID REFERENCES invoices(id) ON DELETE CASCADE,
    description TEXT NOT NULL,
    quantity INTEGER DEFAULT 1,
    unit_price DECIMAL(10,2) NOT NULL,
    total DECIMAL(10,2) NOT NULL,
    item_type VARCHAR(50) CHECK (item_type IN ('subscription', 'overage', 'support', 'custom'))
);

-- Support Tickets
CREATE TABLE support_tickets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_id UUID REFERENCES customers(id) ON DELETE CASCADE,
    subject VARCHAR(255) NOT NULL,
    description TEXT,
    priority VARCHAR(20) DEFAULT 'normal' CHECK (priority IN ('low', 'normal', 'high', 'urgent')),
    status VARCHAR(20) DEFAULT 'open' CHECK (status IN ('open', 'in_progress', 'resolved', 'closed')),
    assigned_to VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP WITH TIME ZONE
);

-- Ticket Messages
CREATE TABLE ticket_messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    ticket_id UUID REFERENCES support_tickets(id) ON DELETE CASCADE,
    sender VARCHAR(50) CHECK (sender IN ('customer', 'support')),
    message TEXT NOT NULL,
    is_internal BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Security Events
CREATE TABLE security_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_id UUID REFERENCES customers(id) ON DELETE CASCADE,
    resource_id UUID REFERENCES infrastructure_resources(id),
    event_type VARCHAR(50) NOT NULL CHECK (event_type IN ('ssh_login', 'failed_login', 'firewall_change', 'vm_start', 'vm_stop', 'config_change')),
    severity VARCHAR(20) DEFAULT 'info' CHECK (severity IN ('info', 'warning', 'critical')),
    description TEXT,
    source_ip VARCHAR(50),
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Audit Logs
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_id UUID REFERENCES customers(id) ON DELETE CASCADE,
    user_id VARCHAR(255),
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50),
    resource_id VARCHAR(255),
    old_values JSONB,
    new_values JSONB,
    ip_address VARCHAR(50),
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- API Keys
CREATE TABLE api_keys (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_id UUID REFERENCES customers(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    key_hash VARCHAR(255) NOT NULL,
    scopes TEXT[],
    last_used TIMESTAMP WITH TIME ZONE,
    expires_at TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Reports
CREATE TABLE reports (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_id UUID REFERENCES customers(id) ON DELETE CASCADE,
    report_type VARCHAR(50) NOT NULL CHECK (report_type IN ('usage', 'security', 'cost', 'performance')),
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    status VARCHAR(20) DEFAULT 'generating' CHECK (status IN ('generating', 'completed', 'failed')),
    file_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE
);

-- Indexes for performance
CREATE INDEX idx_customers_tenant_id ON customers(tenant_id);
CREATE INDEX idx_customers_email ON customers(email);
CREATE INDEX idx_customers_status ON customers(status);
CREATE INDEX idx_subscriptions_customer_id ON subscriptions(customer_id);
CREATE INDEX idx_subscriptions_status ON subscriptions(status);
CREATE INDEX idx_infrastructure_customer_id ON infrastructure_resources(customer_id);
CREATE INDEX idx_infrastructure_resource_id ON infrastructure_resources(resource_id);
CREATE INDEX idx_usage_metrics_customer_id ON usage_metrics(customer_id);
CREATE INDEX idx_usage_metrics_recorded_at ON usage_metrics(recorded_at);
CREATE INDEX idx_invoices_customer_id ON invoices(customer_id);
CREATE INDEX idx_invoices_status ON invoices(status);
CREATE INDEX idx_security_events_customer_id ON security_events(customer_id);
CREATE INDEX idx_security_events_created_at ON security_events(created_at);
CREATE INDEX idx_audit_logs_customer_id ON audit_logs(customer_id);
CREATE INDEX idx_audit_logs_created_at ON audit_logs(created_at);

-- Insert default subscription plans
INSERT INTO subscription_plans (name, tier, monthly_price, annual_price, max_vms, max_users, support_level, features) VALUES
('Basic', 'basic', 500.00, 5000.00, 3, 5, 'email', 
 '{"hardening": true, "monitoring": true, "backup": false, "ssl": false, "support_hours": "9-17"}'::jsonb),
('Professional', 'pro', 1500.00, 15000.00, 10, 20, 'chat',
 '{"hardening": true, "monitoring": true, "backup": true, "ssl": true, "support_hours": "24/7"}'::jsonb),
('Enterprise', 'enterprise', 3000.00, 30000.00, 50, 100, '24/7',
 '{"hardening": true, "monitoring": true, "backup": true, "ssl": true, "support_hours": "24/7", "sla": "99.9", "dedicated_support": true}'::jsonb);

-- Trigger for updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_customers_updated_at BEFORE UPDATE ON customers
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_subscriptions_updated_at BEFORE UPDATE ON subscriptions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_infrastructure_resources_updated_at BEFORE UPDATE ON infrastructure_resources
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_support_tickets_updated_at BEFORE UPDATE ON support_tickets
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
