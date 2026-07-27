"""
Automated Reporting System
Generates security, usage, cost, and performance reports for customers
"""

import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import psycopg2
from psycopg2.extras import RealDictCursor
import json
import pandas as pd
from jinja2 import Template
import pdfkit

logger = logging.getLogger(__name__)


class ReportGenerator:
    """Generates various types of reports for customers"""
    
    def __init__(self):
        self.db_host = os.getenv('DB_HOST', 'localhost')
        self.db_name = os.getenv('DB_NAME', 'infrahardening')
        self.db_user = os.getenv('DB_USER', 'postgres')
        self.db_password = os.getenv('DB_PASSWORD', 'password')
    
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
    
    def generate_security_report(self, customer_id: str, period_start: datetime, 
                                period_end: datetime) -> Dict:
        """Generate security report for a customer"""
        try:
            conn = self.get_db_connection()
            
            with conn.cursor() as cur:
                # Get customer info
                cur.execute("""
                    SELECT * FROM customers WHERE id = %s
                """, (customer_id,))
                customer = cur.fetchone()
                
                # Get security events
                cur.execute("""
                    SELECT * FROM security_events 
                    WHERE customer_id = %s 
                    AND created_at BETWEEN %s AND %s
                    ORDER BY created_at DESC
                """, (customer_id, period_start, period_end))
                security_events = cur.fetchall()
                
                # Get infrastructure status
                cur.execute("""
                    SELECT * FROM infrastructure_resources 
                    WHERE customer_id = %s
                """, (customer_id,))
                resources = cur.fetchall()
                
                # Calculate security metrics
                critical_events = [e for e in security_events if e['severity'] == 'critical']
                warning_events = [e for e in security_events if e['severity'] == 'warning']
                
                report = {
                    'report_type': 'security',
                    'customer': customer['company_name'],
                    'period_start': period_start.strftime('%Y-%m-%d'),
                    'period_end': period_end.strftime('%Y-%m-%d'),
                    'generated_at': datetime.now().isoformat(),
                    'summary': {
                        'total_events': len(security_events),
                        'critical_events': len(critical_events),
                        'warning_events': len(warning_events),
                        'total_resources': len(resources),
                        'secure_resources': len([r for r in resources if r['status'] == 'running'])
                    },
                    'security_events': security_events,
                    'infrastructure_status': resources,
                    'recommendations': self._generate_security_recommendations(security_events, resources)
                }
                
                logger.info(f"Generated security report for customer {customer_id}")
                return report
                
        except Exception as e:
            logger.error(f"Error generating security report: {e}")
            raise
        finally:
            conn.close()
    
    def generate_usage_report(self, customer_id: str, period_start: datetime, 
                             period_end: datetime) -> Dict:
        """Generate usage report for a customer"""
        try:
            conn = self.get_db_connection()
            
            with conn.cursor() as cur:
                # Get customer info
                cur.execute("""
                    SELECT * FROM customers WHERE id = %s
                """, (customer_id,))
                customer = cur.fetchone()
                
                # Get usage metrics
                cur.execute("""
                    SELECT * FROM usage_metrics 
                    WHERE customer_id = %s 
                    AND recorded_at BETWEEN %s AND %s
                    ORDER BY recorded_at DESC
                """, (customer_id, period_start, period_end))
                usage_metrics = cur.fetchall()
                
                # Get infrastructure
                cur.execute("""
                    SELECT * FROM infrastructure_resources 
                    WHERE customer_id = %s
                """, (customer_id,))
                resources = cur.fetchall()
                
                # Calculate usage statistics
                cpu_usage = [m for m in usage_metrics if m['metric_type'] == 'cpu']
                memory_usage = [m for m in usage_metrics if m['metric_type'] == 'memory']
                disk_usage = [m for m in usage_metrics if m['metric_type'] == 'disk']
                
                avg_cpu = sum(m['metric_value'] for m in cpu_usage) / len(cpu_usage) if cpu_usage else 0
                avg_memory = sum(m['metric_value'] for m in memory_usage) / len(memory_usage) if memory_usage else 0
                avg_disk = sum(m['metric_value'] for m in disk_usage) / len(disk_usage) if disk_usage else 0
                
                report = {
                    'report_type': 'usage',
                    'customer': customer['company_name'],
                    'period_start': period_start.strftime('%Y-%m-%d'),
                    'period_end': period_end.strftime('%Y-%m-%d'),
                    'generated_at': datetime.now().isoformat(),
                    'summary': {
                        'total_resources': len(resources),
                        'avg_cpu_usage': round(avg_cpu, 2),
                        'avg_memory_usage': round(avg_memory, 2),
                        'avg_disk_usage': round(avg_disk, 2),
                        'total_metrics': len(usage_metrics)
                    },
                    'usage_metrics': usage_metrics,
                    'resource_usage': self._calculate_resource_usage(usage_metrics, resources),
                    'trends': self._calculate_usage_trends(usage_metrics)
                }
                
                logger.info(f"Generated usage report for customer {customer_id}")
                return report
                
        except Exception as e:
            logger.error(f"Error generating usage report: {e}")
            raise
        finally:
            conn.close()
    
    def generate_cost_report(self, customer_id: str, period_start: datetime, 
                            period_end: datetime) -> Dict:
        """Generate cost report for a customer"""
        try:
            conn = self.get_db_connection()
            
            with conn.cursor() as cur:
                # Get customer info
                cur.execute("""
                    SELECT c.*, s.plan_id, sp.monthly_price, sp.name as plan_name
                    FROM customers c
                    LEFT JOIN subscriptions s ON c.id = s.customer_id AND s.status = 'active'
                    LEFT JOIN subscription_plans sp ON s.plan_id = sp.id
                    WHERE c.id = %s
                """, (customer_id,))
                customer = cur.fetchone()
                
                # Get invoices
                cur.execute("""
                    SELECT * FROM invoices 
                    WHERE customer_id = %s 
                    AND created_at BETWEEN %s AND %s
                    ORDER BY created_at DESC
                """, (customer_id, period_start, period_end))
                invoices = cur.fetchall()
                
                # Get infrastructure
                cur.execute("""
                    SELECT * FROM infrastructure_resources 
                    WHERE customer_id = %s
                """, (customer_id,))
                resources = cur.fetchall()
                
                # Calculate cost metrics
                total_invoiced = sum(inv['amount'] for inv in invoices)
                paid_invoices = [inv for inv in invoices if inv['status'] == 'paid']
                pending_invoices = [inv for inv in invoices if inv['status'] == 'pending']
                overdue_invoices = [inv for inv in invoices if inv['status'] == 'overdue']
                
                report = {
                    'report_type': 'cost',
                    'customer': customer['company_name'],
                    'period_start': period_start.strftime('%Y-%m-%d'),
                    'period_end': period_end.strftime('%Y-%m-%d'),
                    'generated_at': datetime.now().isoformat(),
                    'summary': {
                        'plan': customer['plan_name'],
                        'monthly_cost': customer['monthly_price'],
                        'total_invoiced': total_invoiced,
                        'total_paid': sum(inv['amount'] for inv in paid_invoices),
                        'total_pending': sum(inv['amount'] for inv in pending_invoices),
                        'total_overdue': sum(inv['amount'] for inv in overdue_invoices),
                        'total_resources': len(resources)
                    },
                    'invoices': invoices,
                    'cost_breakdown': self._calculate_cost_breakdown(resources),
                    'recommendations': self._generate_cost_recommendations(invoices, resources)
                }
                
                logger.info(f"Generated cost report for customer {customer_id}")
                return report
                
        except Exception as e:
            logger.error(f"Error generating cost report: {e}")
            raise
        finally:
            conn.close()
    
    def generate_performance_report(self, customer_id: str, period_start: datetime, 
                                    period_end: datetime) -> Dict:
        """Generate performance report for a customer"""
        try:
            conn = self.get_db_connection()
            
            with conn.cursor() as cur:
                # Get customer info
                cur.execute("""
                    SELECT * FROM customers WHERE id = %s
                """, (customer_id,))
                customer = cur.fetchone()
                
                # Get usage metrics for performance analysis
                cur.execute("""
                    SELECT * FROM usage_metrics 
                    WHERE customer_id = %s 
                    AND recorded_at BETWEEN %s AND %s
                    ORDER BY recorded_at ASC
                """, (customer_id, period_start, period_end))
                metrics = cur.fetchall()
                
                # Get infrastructure
                cur.execute("""
                    SELECT * FROM infrastructure_resources 
                    WHERE customer_id = %s
                """, (customer_id,))
                resources = cur.fetchall()
                
                # Calculate performance metrics
                report = {
                    'report_type': 'performance',
                    'customer': customer['company_name'],
                    'period_start': period_start.strftime('%Y-%m-%d'),
                    'period_end': period_end.strftime('%Y-%m-%d'),
                    'generated_at': datetime.now().isoformat(),
                    'summary': {
                        'total_resources': len(resources),
                        'uptime_percentage': self._calculate_uptime(resources, metrics),
                        'avg_response_time': self._calculate_avg_response_time(metrics),
                        'performance_score': self._calculate_performance_score(resources, metrics)
                    },
                    'resource_performance': self._analyze_resource_performance(resources, metrics),
                    'trends': self._calculate_performance_trends(metrics),
                    'recommendations': self._generate_performance_recommendations(resources, metrics)
                }
                
                logger.info(f"Generated performance report for customer {customer_id}")
                return report
                
        except Exception as e:
            logger.error(f"Error generating performance report: {e}")
            raise
        finally:
            conn.close()
    
    def _generate_security_recommendations(self, events: List, resources: List) -> List:
        """Generate security recommendations based on events"""
        recommendations = []
        
        critical_events = [e for e in events if e['severity'] == 'critical']
        if len(critical_events) > 5:
            recommendations.append({
                'priority': 'high',
                'issue': 'Wysoka liczba zdarzeń krytycznych',
                'recommendation': 'Rozważ zwiększenie poziomu monitoringu i wdrożenie dodatkowych zabezpieczeń'
            })
        
        failed_logins = [e for e in events if 'failed_login' in str(e.get('event_type', ''))]
        if len(failed_logins) > 10:
            recommendations.append({
                'priority': 'medium',
                'issue': 'Wielu nieudanych prób logowania',
                'recommendation': 'Rozważ wdrożenie dodatkowych mechanizmów ochrony przed atakami brute-force'
            })
        
        return recommendations
    
    def _calculate_resource_usage(self, metrics: List, resources: List) -> Dict:
        """Calculate per-resource usage statistics"""
        resource_usage = {}
        
        for resource in resources:
            resource_id = resource['id']
            resource_metrics = [m for m in metrics if m['resource_id'] == resource_id]
            
            if resource_metrics:
                cpu_metrics = [m for m in resource_metrics if m['metric_type'] == 'cpu']
                memory_metrics = [m for m in resource_metrics if m['metric_type'] == 'memory']
                
                resource_usage[resource['resource_name']] = {
                    'avg_cpu': sum(m['metric_value'] for m in cpu_metrics) / len(cpu_metrics) if cpu_metrics else 0,
                    'avg_memory': sum(m['metric_value'] for m in memory_metrics) / len(memory_metrics) if memory_metrics else 0,
                    'total_metrics': len(resource_metrics)
                }
        
        return resource_usage
    
    def _calculate_usage_trends(self, metrics: List) -> Dict:
        """Calculate usage trends over time"""
        # Simplified trend calculation
        if len(metrics) < 2:
            return {'trend': 'insufficient_data'}
        
        recent_metrics = metrics[:len(metrics)//2]
        older_metrics = metrics[len(metrics)//2:]
        
        recent_avg = sum(m['metric_value'] for m in recent_metrics) / len(recent_metrics)
        older_avg = sum(m['metric_value'] for m in older_metrics) / len(older_metrics)
        
        if recent_avg > older_avg * 1.1:
            trend = 'increasing'
        elif recent_avg < older_avg * 0.9:
            trend = 'decreasing'
        else:
            trend = 'stable'
        
        return {'trend': trend, 'change_percent': round((recent_avg - older_avg) / older_avg * 100, 2)}
    
    def _calculate_cost_breakdown(self, resources: List) -> Dict:
        """Calculate cost breakdown by resource type"""
        breakdown = {}
        
        for resource in resources:
            resource_type = resource['resource_type']
            monthly_cost = resource.get('monthly_cost', 0)
            
            if resource_type not in breakdown:
                breakdown[resource_type] = {'count': 0, 'total_cost': 0}
            
            breakdown[resource_type]['count'] += 1
            breakdown[resource_type]['total_cost'] += monthly_cost
        
        return breakdown
    
    def _generate_cost_recommendations(self, invoices: List, resources: List) -> List:
        """Generate cost optimization recommendations"""
        recommendations = []
        
        overdue_invoices = [inv for inv in invoices if inv['status'] == 'overdue']
        if overdue_invoices:
            recommendations.append({
                'priority': 'high',
                'issue': 'Zaległe płatności',
                'recommendation': 'Skontaktuj się z klientem w sprawie zaległych płatności'
            })
        
        return recommendations
    
    def _calculate_uptime(self, resources: List, metrics: List) -> float:
        """Calculate overall uptime percentage"""
        # Simplified uptime calculation
        running_resources = len([r for r in resources if r['status'] == 'running'])
        total_resources = len(resources)
        
        if total_resources == 0:
            return 0.0
        
        return round((running_resources / total_resources) * 100, 2)
    
    def _calculate_avg_response_time(self, metrics: List) -> float:
        """Calculate average response time"""
        # Simplified - would need actual response time metrics
        return 0.0
    
    def _calculate_performance_score(self, resources: List, metrics: List) -> float:
        """Calculate overall performance score"""
        uptime = self._calculate_uptime(resources, metrics)
        
        # Simple scoring based on uptime
        if uptime >= 99.9:
            return 100.0
        elif uptime >= 99.5:
            return 95.0
        elif uptime >= 99.0:
            return 90.0
        else:
            return uptime
    
    def _analyze_resource_performance(self, resources: List, metrics: List) -> Dict:
        """Analyze performance per resource"""
        performance = {}
        
        for resource in resources:
            resource_metrics = [m for m in metrics if m['resource_id'] == resource['id']]
            
            if resource_metrics:
                performance[resource['resource_name']] = {
                    'status': resource['status'],
                    'metric_count': len(resource_metrics),
                    'last_updated': max(m['recorded_at'] for m in resource_metrics) if resource_metrics else None
                }
        
        return performance
    
    def _calculate_performance_trends(self, metrics: List) -> Dict:
        """Calculate performance trends"""
        return self._calculate_usage_trends(metrics)
    
    def _generate_performance_recommendations(self, resources: List, metrics: List) -> List:
        """Generate performance optimization recommendations"""
        recommendations = []
        
        stopped_resources = [r for r in resources if r['status'] == 'stopped']
        if stopped_resources:
            recommendations.append({
                'priority': 'medium',
                'issue': 'Zatrzymane zasoby',
                'recommendation': 'Rozważ restart zatrzymanych zasobów lub ich usunięcie jeśli nie są potrzebne'
            })
        
        return recommendations
    
    def save_report_to_db(self, customer_id: str, report_type: str, 
                         period_start: datetime, period_end: datetime, 
                         report_data: Dict) -> str:
        """Save report to database"""
        try:
            conn = self.get_db_connection()
            
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO reports (customer_id, report_type, period_start, period_end, status)
                    VALUES (%s, %s, %s, %s, 'generating')
                    RETURNING id
                """, (customer_id, report_type, period_start, period_end))
                report_id = cur.fetchone()['id']
                
                # In production, save report_data to file storage and update file_url
                cur.execute("""
                    UPDATE reports 
                    SET status = 'completed', completed_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                """, (report_id,))
                
                conn.commit()
                
                logger.info(f"Saved report {report_id} to database")
                return report_id
                
        except Exception as e:
            logger.error(f"Error saving report to database: {e}")
            raise
        finally:
            conn.close()
    
    def generate_pdf_report(self, report_data: Dict, template_path: str = None) -> bytes:
        """Generate PDF report from data"""
        try:
            # Use Jinja2 template to generate HTML
            if template_path:
                with open(template_path, 'r') as f:
                    template = Template(f.read())
            else:
                # Default template
                template = Template("""
                <html>
                <head>
                    <style>
                        body { font-family: Arial, sans-serif; margin: 20px; }
                        h1 { color: #333; }
                        .summary { background: #f5f5f5; padding: 15px; margin: 20px 0; }
                        .metric { margin: 10px 0; }
                    </style>
                </head>
                <body>
                    <h1>{{ report_type|title }} Report</h1>
                    <p>Customer: {{ customer }}</p>
                    <p>Period: {{ period_start }} to {{ period_end }}</p>
                    <div class="summary">
                        <h2>Summary</h2>
                        {% for key, value in summary.items() %}
                        <div class="metric"><strong>{{ key }}:</strong> {{ value }}</div>
                        {% endfor %}
                    </div>
                </body>
                </html>
                """)
            
            html_content = template.render(**report_data)
            
            # Convert to PDF
            pdf_content = pdfkit.from_string(html_content, False)
            
            return pdf_content
            
        except Exception as e:
            logger.error(f"Error generating PDF report: {e}")
            raise


# Scheduler for automated report generation
class ReportScheduler:
    """Schedules automated report generation"""
    
    def __init__(self):
        self.generator = ReportGenerator()
    
    def generate_monthly_reports(self):
        """Generate monthly reports for all active customers"""
        try:
            conn = self.generator.get_db_connection()
            
            with conn.cursor() as cur:
                # Get all active customers
                cur.execute("""
                    SELECT id FROM customers WHERE status = 'active'
                """)
                customers = cur.fetchall()
                
                period_end = datetime.now()
                period_start = period_end - timedelta(days=30)
                
                for customer in customers:
                    customer_id = customer['id']
                    
                    # Generate different types of reports
                    report_types = ['security', 'usage', 'cost', 'performance']
                    
                    for report_type in report_types:
                        try:
                            if report_type == 'security':
                                report_data = self.generator.generate_security_report(
                                    customer_id, period_start, period_end
                                )
                            elif report_type == 'usage':
                                report_data = self.generator.generate_usage_report(
                                    customer_id, period_start, period_end
                                )
                            elif report_type == 'cost':
                                report_data = self.generator.generate_cost_report(
                                    customer_id, period_start, period_end
                                )
                            elif report_type == 'performance':
                                report_data = self.generator.generate_performance_report(
                                    customer_id, period_start, period_end
                                )
                            
                            # Save to database
                            self.generator.save_report_to_db(
                                customer_id, report_type, period_start, period_end, report_data
                            )
                            
                            logger.info(f"Generated {report_type} report for customer {customer_id}")
                            
                        except Exception as e:
                            logger.error(f"Error generating {report_type} report for customer {customer_id}: {e}")
                            continue
                
                conn.close()
                
        except Exception as e:
            logger.error(f"Error in monthly report generation: {e}")
            raise


if __name__ == '__main__':
    # Generate reports for all customers
    scheduler = ReportScheduler()
    scheduler.generate_monthly_reports()
