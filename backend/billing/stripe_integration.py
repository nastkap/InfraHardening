"""
Stripe Payment Integration
Handles payment processing, subscriptions, and invoicing
"""

import os
import stripe
from datetime import datetime, timedelta
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)

# Initialize Stripe
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

class StripeService:
    """Service for Stripe payment operations"""
    
    def __init__(self):
        self.webhook_secret = os.getenv('STRIPE_WEBHOOK_SECRET')
    
    def create_customer(self, email: str, name: str, metadata: Dict = None) -> stripe.Customer:
        """Create a new Stripe customer"""
        try:
            customer = stripe.Customer.create(
                email=email,
                name=name,
                metadata=metadata or {}
            )
            logger.info(f"Created Stripe customer: {customer.id}")
            return customer
        except stripe.error.StripeError as e:
            logger.error(f"Error creating Stripe customer: {e}")
            raise
    
    def create_product(self, name: str, description: str, metadata: Dict = None) -> stripe.Product:
        """Create a Stripe product"""
        try:
            product = stripe.Product.create(
                name=name,
                description=description,
                metadata=metadata or {}
            )
            logger.info(f"Created Stripe product: {product.id}")
            return product
        except stripe.error.StripeError as e:
            logger.error(f"Error creating Stripe product: {e}")
            raise
    
    def create_price(self, product_id: str, amount: int, currency: str = 'pln', 
                    interval: str = 'month') -> stripe.Price:
        """Create a Stripe price"""
        try:
            price = stripe.Price.create(
                product=product_id,
                unit_amount=amount * 100,  # Stripe uses cents
                currency=currency,
                recurring={'interval': interval}
            )
            logger.info(f"Created Stripe price: {price.id}")
            return price
        except stripe.error.StripeError as e:
            logger.error(f"Error creating Stripe price: {e}")
            raise
    
    def create_subscription(self, customer_id: str, price_id: str, 
                           trial_period_days: int = None) -> stripe.Subscription:
        """Create a subscription for a customer"""
        try:
            subscription_data = {
                'customer': customer_id,
                'items': [{'price': price_id}],
                'payment_behavior': 'default_incomplete',
            }
            
            if trial_period_days:
                subscription_data['trial_period_days'] = trial_period_days
            
            subscription = stripe.Subscription.create(**subscription_data)
            logger.info(f"Created Stripe subscription: {subscription.id}")
            return subscription
        except stripe.error.StripeError as e:
            logger.error(f"Error creating Stripe subscription: {e}")
            raise
    
    def create_checkout_session(self, customer_id: str, price_id: str, 
                               success_url: str, cancel_url: str) -> stripe.checkout.Session:
        """Create a Stripe Checkout session"""
        try:
            session = stripe.checkout.Session.create(
                customer=customer_id,
                payment_method_types=['card'],
                line_items=[{'price': price_id, 'quantity': 1}],
                mode='subscription',
                success_url=success_url,
                cancel_url=cancel_url
            )
            logger.info(f"Created Stripe checkout session: {session.id}")
            return session
        except stripe.error.StripeError as e:
            logger.error(f"Error creating checkout session: {e}")
            raise
    
    def create_invoice(self, customer_id: str, description: str = None) -> stripe.Invoice:
        """Create an invoice for a customer"""
        try:
            invoice = stripe.Invoice.create(
                customer=customer_id,
                description=description,
                auto_advance=True
            )
            logger.info(f"Created Stripe invoice: {invoice.id}")
            return invoice
        except stripe.error.StripeError as e:
            logger.error(f"Error creating invoice: {e}")
            raise
    
    def send_invoice(self, invoice_id: str) -> stripe.Invoice:
        """Send an invoice to customer"""
        try:
            invoice = stripe.Invoice.send_invoice(invoice_id)
            logger.info(f"Sent Stripe invoice: {invoice_id}")
            return invoice
        except stripe.error.StripeError as e:
            logger.error(f"Error sending invoice: {e}")
            raise
    
    def cancel_subscription(self, subscription_id: str, at_period_end: bool = True) -> stripe.Subscription:
        """Cancel a subscription"""
        try:
            subscription = stripe.Subscription.modify(
                subscription_id,
                cancel_at_period_end=at_period_end
            )
            logger.info(f"Cancelled Stripe subscription: {subscription_id}")
            return subscription
        except stripe.error.StripeError as e:
            logger.error(f"Error cancelling subscription: {e}")
            raise
    
    def update_subscription(self, subscription_id: str, price_id: str) -> stripe.Subscription:
        """Update subscription to a different price"""
        try:
            subscription = stripe.Subscription.retrieve(subscription_id)
            
            # Update the subscription item
            updated_subscription = stripe.Subscription.modify(
                subscription_id,
                items=[{
                    'id': subscription['items']['data'][0].id,
                    'price': price_id
                }]
            )
            logger.info(f"Updated Stripe subscription: {subscription_id}")
            return updated_subscription
        except stripe.error.StripeError as e:
            logger.error(f"Error updating subscription: {e}")
            raise
    
    def handle_webhook(self, payload: str, sig_header: str) -> Dict:
        """Handle Stripe webhook events"""
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, self.webhook_secret
            )
            
            logger.info(f"Received Stripe webhook: {event['type']}")
            
            # Handle different event types
            if event['type'] == 'checkout.session.completed':
                return self._handle_checkout_completed(event)
            elif event['type'] == 'invoice.paid':
                return self._handle_invoice_paid(event)
            elif event['type'] == 'invoice.payment_failed':
                return self._handle_payment_failed(event)
            elif event['type'] == 'customer.subscription.deleted':
                return self._handle_subscription_deleted(event)
            elif event['type'] == 'customer.subscription.updated':
                return self._handle_subscription_updated(event)
            
            return {'status': 'success', 'message': 'Event received'}
            
        except ValueError as e:
            logger.error(f"Invalid payload: {e}")
            raise
        except stripe.error.SignatureVerificationError as e:
            logger.error(f"Invalid signature: {e}")
            raise
    
    def _handle_checkout_completed(self, event) -> Dict:
        """Handle checkout.session.completed event"""
        session = event['data']['object']
        logger.info(f"Checkout completed for customer: {session['customer']}")
        
        return {
            'status': 'success',
            'event': 'checkout.completed',
            'customer_id': session['customer'],
            'subscription_id': session.get('subscription')
        }
    
    def _handle_invoice_paid(self, event) -> Dict:
        """Handle invoice.paid event"""
        invoice = event['data']['object']
        logger.info(f"Invoice paid: {invoice['id']} for customer: {invoice['customer']}")
        
        return {
            'status': 'success',
            'event': 'invoice.paid',
            'invoice_id': invoice['id'],
            'customer_id': invoice['customer'],
            'amount': invoice['amount_paid'] / 100
        }
    
    def _handle_payment_failed(self, event) -> Dict:
        """Handle invoice.payment_failed event"""
        invoice = event['data']['object']
        logger.warning(f"Payment failed for invoice: {invoice['id']}")
        
        return {
            'status': 'failed',
            'event': 'invoice.payment_failed',
            'invoice_id': invoice['id'],
            'customer_id': invoice['customer']
        }
    
    def _handle_subscription_deleted(self, event) -> Dict:
        """Handle customer.subscription.deleted event"""
        subscription = event['data']['object']
        logger.info(f"Subscription deleted: {subscription['id']}")
        
        return {
            'status': 'success',
            'event': 'subscription.deleted',
            'subscription_id': subscription['id'],
            'customer_id': subscription['customer']
        }
    
    def _handle_subscription_updated(self, event) -> Dict:
        """Handle customer.subscription.updated event"""
        subscription = event['data']['object']
        logger.info(f"Subscription updated: {subscription['id']}")
        
        return {
            'status': 'success',
            'event': 'subscription.updated',
            'subscription_id': subscription['id'],
            'customer_id': subscription['customer'],
            'status': subscription['status']
        }
    
    def get_customer_invoices(self, customer_id: str, limit: int = 10) -> list:
        """Get invoices for a customer"""
        try:
            invoices = stripe.Invoice.list(
                customer=customer_id,
                limit=limit
            )
            return invoices['data']
        except stripe.error.StripeError as e:
            logger.error(f"Error getting invoices: {e}")
            raise
    
    def get_usage_records(self, subscription_item_id: str) -> list:
        """Get usage records for a subscription item"""
        try:
            usage = stripe.UsageRecord.list(
                subscription_item=subscription_item_id,
                limit=100
            )
            return usage['data']
        except stripe.error.StripeError as e:
            logger.error(f"Error getting usage records: {e}")
            raise


# Initialize Stripe products and prices
def initialize_stripe_products():
    """Initialize Stripe products and prices based on pricing config"""
    import yaml
    
    try:
        with open('backend/config/pricing.yaml', 'r') as f:
            pricing_config = yaml.safe_load(f)
        
        stripe_service = StripeService()
        
        for plan_key, plan_config in pricing_config['plans'].items():
            # Create product
            product = stripe_service.create_product(
                name=plan_config['name'],
                description=plan_config['description'],
                metadata={'tier': plan_config['tier']}
            )
            
            # Create monthly price
            stripe_service.create_price(
                product_id=product.id,
                amount=plan_config['monthly_price'],
                currency=plan_config['currency'],
                interval='month'
            )
            
            # Create annual price
            stripe_service.create_price(
                product_id=product.id,
                amount=plan_config['annual_price'] / 12,  # Monthly equivalent
                currency=plan_config['currency'],
                interval='year'
            )
            
            logger.info(f"Initialized Stripe product for plan: {plan_key}")
        
        logger.info("Stripe products initialized successfully")
        
    except Exception as e:
        logger.error(f"Error initializing Stripe products: {e}")
        raise


if __name__ == '__main__':
    # Initialize Stripe products
    initialize_stripe_products()
