"""
Billing Manager
Coordinates between different payment providers and internal billing system
"""

from typing import Dict, Optional
import logging
from datetime import datetime, date
import uuid

from stripe_integration import StripeService
from przelewy24_integration import Przelewy24Service

logger = logging.getLogger(__name__)


class BillingManager:
    """Manages billing operations across payment providers"""
    
    def __init__(self):
        self.stripe_service = StripeService()
        self.p24_service = Przelewy24Service()
    
    def create_payment_method(self, provider: str, customer_data: Dict) -> Dict:
        """Create payment method for customer"""
        try:
            if provider == 'stripe':
                stripe_customer = self.stripe_service.create_customer(
                    email=customer_data['email'],
                    name=customer_data['name'],
                    metadata={'customer_id': str(customer_data['id'])}
                )
                return {
                    'success': True,
                    'provider': 'stripe',
                    'customer_id': stripe_customer.id
                }
            elif provider == 'przelewy24':
                # Przelewy24 doesn't require customer creation upfront
                return {
                    'success': True,
                    'provider': 'przelewy24',
                    'customer_id': customer_data['id']
                }
            else:
                return {'success': False, 'error': 'Unsupported payment provider'}
                
        except Exception as e:
            logger.error(f"Error creating payment method: {e}")
            return {'success': False, 'error': str(e)}
    
    def create_subscription_payment(self, provider: str, subscription_data: Dict) -> Dict:
        """Create subscription payment"""
        try:
            if provider == 'stripe':
                session = self.stripe_service.create_checkout_session(
                    customer_id=subscription_data['payment_customer_id'],
                    price_id=subscription_data['price_id'],
                    success_url=subscription_data['success_url'],
                    cancel_url=subscription_data['cancel_url']
                )
                return {
                    'success': True,
                    'provider': 'stripe',
                    'checkout_url': session.url,
                    'session_id': session.id
                }
            elif provider == 'przelewy24':
                result = self.p24_service.register_transaction(
                    session_id=subscription_data['session_id'],
                    amount=subscription_data['amount'],
                    description=subscription_data['description'],
                    email=subscription_data['email'],
                    return_url=subscription_data['return_url']
                )
                return result
            else:
                return {'success': False, 'error': 'Unsupported payment provider'}
                
        except Exception as e:
            logger.error(f"Error creating subscription payment: {e}")
            return {'success': False, 'error': str(e)}
    
    def create_invoice(self, customer_id: str, amount: float, 
                      description: str, provider: str = 'stripe') -> Dict:
        """Create invoice for customer"""
        try:
            if provider == 'stripe':
                invoice = self.stripe_service.create_invoice(
                    customer_id=customer_id,
                    description=description
                )
                return {
                    'success': True,
                    'provider': 'stripe',
                    'invoice_id': invoice.id,
                    'amount': invoice.total / 100,
                    'currency': invoice.currency,
                    'status': invoice.status
                }
            else:
                # For other providers, create internal invoice
                invoice_id = f"INV-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"
                return {
                    'success': True,
                    'provider': provider,
                    'invoice_id': invoice_id,
                    'amount': amount,
                    'currency': 'PLN',
                    'status': 'pending'
                }
                
        except Exception as e:
            logger.error(f"Error creating invoice: {e}")
            return {'success': False, 'error': str(e)}
    
    def send_invoice(self, invoice_id: str, provider: str = 'stripe') -> Dict:
        """Send invoice to customer"""
        try:
            if provider == 'stripe':
                invoice = self.stripe_service.send_invoice(invoice_id)
                return {
                    'success': True,
                    'invoice_id': invoice.id,
                    'status': invoice.status
                }
            else:
                # For other providers, mark as sent internally
                return {
                    'success': True,
                    'invoice_id': invoice_id,
                    'status': 'sent'
                }
                
        except Exception as e:
            logger.error(f"Error sending invoice: {e}")
            return {'success': False, 'error': str(e)}
    
    def cancel_subscription(self, subscription_id: str, provider: str = 'stripe') -> Dict:
        """Cancel subscription"""
        try:
            if provider == 'stripe':
                subscription = self.stripe_service.cancel_subscription(subscription_id)
                return {
                    'success': True,
                    'subscription_id': subscription.id,
                    'cancel_at_period_end': subscription.cancel_at_period_end
                }
            else:
                # For other providers, handle internally
                return {
                    'success': True,
                    'subscription_id': subscription_id,
                    'cancelled': True
                }
                
        except Exception as e:
            logger.error(f"Error cancelling subscription: {e}")
            return {'success': False, 'error': str(e)}
    
    def update_subscription(self, subscription_id: str, new_price_id: str, 
                           provider: str = 'stripe') -> Dict:
        """Update subscription to different plan"""
        try:
            if provider == 'stripe':
                subscription = self.stripe_service.update_subscription(
                    subscription_id, new_price_id
                )
                return {
                    'success': True,
                    'subscription_id': subscription.id,
                    'status': subscription.status
                }
            else:
                # For other providers, handle internally
                return {
                    'success': True,
                    'subscription_id': subscription_id,
                    'updated': True
                }
                
        except Exception as e:
            logger.error(f"Error updating subscription: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_payment_status(self, payment_id: str, provider: str) -> Dict:
        """Get payment status"""
        try:
            if provider == 'stripe':
                # For Stripe, get payment intent or invoice
                payment_intent = stripe.PaymentIntent.retrieve(payment_id)
                return {
                    'success': True,
                    'status': payment_intent.status,
                    'amount': payment_intent.amount / 100
                }
            elif provider == 'przelewy24':
                status = self.p24_service.get_transaction_status(payment_id)
                return status
            else:
                return {'success': False, 'error': 'Unsupported payment provider'}
                
        except Exception as e:
            logger.error(f"Error getting payment status: {e}")
            return {'success': False, 'error': str(e)}
    
    def handle_webhook(self, provider: str, payload: str, 
                      signature: str = None) -> Dict:
        """Handle webhook from payment provider"""
        try:
            if provider == 'stripe':
                return self.stripe_service.handle_webhook(payload, signature)
            elif provider == 'przelewy24':
                # Handle Przelewy24 webhook
                return self._handle_p24_webhook(payload)
            else:
                return {'success': False, 'error': 'Unsupported payment provider'}
                
        except Exception as e:
            logger.error(f"Error handling webhook: {e}")
            return {'success': False, 'error': str(e)}
    
    def _handle_p24_webhook(self, payload: str) -> Dict:
        """Handle Przelewy24 webhook"""
        # Parse and handle P24 webhook
        # This would need specific implementation based on P24 webhook format
        return {
            'status': 'success',
            'message': 'P24 webhook received'
        }
