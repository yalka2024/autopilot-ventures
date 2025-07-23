#!/usr/bin/env python3
"""
Stripe Webhook Handler for AutoPilot Ventures
Multi-currency payment processing with 10 language support
"""

import os
import json
import logging
import stripe
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime
from flask import Flask, request, jsonify
from dataclasses import dataclass
import hmac
import hashlib

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Load environment variables
stripe.api_key = os.getenv('STRIPE_SECRET_KEY', '')
webhook_secret = os.getenv('STRIPE_WEBHOOK_SECRET', '')

# Multi-currency configuration
SUPPORTED_CURRENCIES = {
    'USD': {'symbol': '$', 'name': 'US Dollar'},
    'EUR': {'symbol': '€', 'name': 'Euro'},
    'GBP': {'symbol': '£', 'name': 'British Pound'},
    'JPY': {'symbol': '¥', 'name': 'Japanese Yen'},
    'CAD': {'symbol': 'C$', 'name': 'Canadian Dollar'},
    'AUD': {'symbol': 'A$', 'name': 'Australian Dollar'},
    'CHF': {'symbol': 'CHF', 'name': 'Swiss Franc'},
    'CNY': {'symbol': '¥', 'name': 'Chinese Yuan'},
    'INR': {'symbol': '₹', 'name': 'Indian Rupee'},
    'BRL': {'symbol': 'R$', 'name': 'Brazilian Real'}
}

# Language-specific currency mappings
LANGUAGE_CURRENCIES = {
    'en': 'USD',  # English - US Dollar
    'es': 'EUR',  # Spanish - Euro
    'zh': 'CNY',  # Chinese - Yuan
    'fr': 'EUR',  # French - Euro
    'de': 'EUR',  # German - Euro
    'ar': 'USD',  # Arabic - US Dollar
    'pt': 'BRL',  # Portuguese - Brazilian Real
    'hi': 'INR',  # Hindi - Indian Rupee
    'ru': 'USD',  # Russian - US Dollar
    'ja': 'JPY'   # Japanese - Yen
}

# Language-specific payment messages
PAYMENT_MESSAGES = {
    'en': {
        'payment_success': 'Payment successful',
        'payment_failed': 'Payment failed',
        'refund_processed': 'Refund processed',
        'subscription_created': 'Subscription created',
        'subscription_cancelled': 'Subscription cancelled'
    },
    'es': {
        'payment_success': 'Pago exitoso',
        'payment_failed': 'Pago fallido',
        'refund_processed': 'Reembolso procesado',
        'subscription_created': 'Suscripción creada',
        'subscription_cancelled': 'Suscripción cancelada'
    },
    'zh': {
        'payment_success': '支付成功',
        'payment_failed': '支付失败',
        'refund_processed': '退款已处理',
        'subscription_created': '订阅已创建',
        'subscription_cancelled': '订阅已取消'
    },
    'fr': {
        'payment_success': 'Paiement réussi',
        'payment_failed': 'Paiement échoué',
        'refund_processed': 'Remboursement traité',
        'subscription_created': 'Abonnement créé',
        'subscription_cancelled': 'Abonnement annulé'
    },
    'de': {
        'payment_success': 'Zahlung erfolgreich',
        'payment_failed': 'Zahlung fehlgeschlagen',
        'refund_processed': 'Rückerstattung verarbeitet',
        'subscription_created': 'Abonnement erstellt',
        'subscription_cancelled': 'Abonnement gekündigt'
    },
    'ar': {
        'payment_success': 'تم الدفع بنجاح',
        'payment_failed': 'فشل الدفع',
        'refund_processed': 'تمت معالجة الاسترداد',
        'subscription_created': 'تم إنشاء الاشتراك',
        'subscription_cancelled': 'تم إلغاء الاشتراك'
    },
    'pt': {
        'payment_success': 'Pagamento bem-sucedido',
        'payment_failed': 'Pagamento falhou',
        'refund_processed': 'Reembolso processado',
        'subscription_created': 'Assinatura criada',
        'subscription_cancelled': 'Assinatura cancelada'
    },
    'hi': {
        'payment_success': 'भुगतान सफल',
        'payment_failed': 'भुगतान विफल',
        'refund_processed': 'धनवापसी संसाधित',
        'subscription_created': 'सदस्यता बनाई गई',
        'subscription_cancelled': 'सदस्यता रद्द'
    },
    'ru': {
        'payment_success': 'Платеж успешен',
        'payment_failed': 'Платеж не удался',
        'refund_processed': 'Возврат обработан',
        'subscription_created': 'Подписка создана',
        'subscription_cancelled': 'Подписка отменена'
    },
    'ja': {
        'payment_success': '支払い成功',
        'payment_failed': '支払い失敗',
        'refund_processed': '返金処理済み',
        'subscription_created': 'サブスクリプション作成',
        'subscription_cancelled': 'サブスクリプションキャンセル'
    }
}


@dataclass
class PaymentEvent:
    """Payment event data structure."""
    event_id: str
    event_type: str
    customer_id: str
    amount: float
    currency: str
    language: str
    metadata: Dict[str, Any]
    timestamp: datetime
    status: str


class MultiCurrencyPaymentProcessor:
    """Multi-currency payment processor with language support."""
    
    def __init__(self):
        self.supported_currencies = SUPPORTED_CURRENCIES
        self.language_currencies = LANGUAGE_CURRENCIES
        self.payment_messages = PAYMENT_MESSAGES
    
    def get_currency_for_language(self, language: str) -> str:
        """Get default currency for a language."""
        return self.language_currencies.get(language, 'USD')
    
    def format_amount(self, amount: float, currency: str, language: str = 'en') -> str:
        """Format amount with currency symbol and language-specific formatting."""
        currency_info = self.supported_currencies.get(currency, {})
        symbol = currency_info.get('symbol', '$')
        
        # Language-specific formatting
        if language in ['zh', 'ja']:
            # Asian formatting: symbol after amount
            return f"{amount:,.2f}{symbol}"
        elif language in ['ar']:
            # Arabic formatting: right-to-left
            return f"{symbol}{amount:,.2f}"
        else:
            # Western formatting: symbol before amount
            return f"{symbol}{amount:,.2f}"
    
    def get_payment_message(self, message_key: str, language: str) -> str:
        """Get localized payment message."""
        messages = self.payment_messages.get(language, self.payment_messages['en'])
        return messages.get(message_key, messages.get('payment_success', 'Payment processed'))
    
    async def process_payment_event(self, event_data: Dict[str, Any]) -> PaymentEvent:
        """Process a payment event with multi-currency support."""
        try:
            # Extract event data
            event_id = event_data.get('id', '')
            event_type = event_data.get('type', '')
            data = event_data.get('data', {})
            object_data = data.get('object', {})
            
            # Extract payment information
            customer_id = object_data.get('customer', '')
            amount = object_data.get('amount', 0) / 100  # Convert from cents
            currency = object_data.get('currency', 'usd').upper()
            metadata = object_data.get('metadata', {})
            
            # Determine language from metadata or default to English
            language = metadata.get('language', 'en')
            
            # Validate currency
            if currency not in self.supported_currencies:
                currency = self.get_currency_for_language(language)
            
            # Create payment event
            payment_event = PaymentEvent(
                event_id=event_id,
                event_type=event_type,
                customer_id=customer_id,
                amount=amount,
                currency=currency,
                language=language,
                metadata=metadata,
                timestamp=datetime.utcnow(),
                status='processed'
            )
            
            # Process based on event type
            await self._handle_event_type(payment_event)
            
            return payment_event
            
        except Exception as e:
            logger.error(f"Error processing payment event: {e}")
            raise
    
    async def _handle_event_type(self, payment_event: PaymentEvent):
        """Handle different event types."""
        event_type = payment_event.event_type
        
        if event_type == 'payment_intent.succeeded':
            await self._handle_payment_success(payment_event)
        elif event_type == 'payment_intent.payment_failed':
            await self._handle_payment_failure(payment_event)
        elif event_type == 'charge.refunded':
            await self._handle_refund(payment_event)
        elif event_type == 'customer.subscription.created':
            await self._handle_subscription_created(payment_event)
        elif event_type == 'customer.subscription.deleted':
            await self._handle_subscription_cancelled(payment_event)
        else:
            logger.info(f"Unhandled event type: {event_type}")
    
    async def _handle_payment_success(self, payment_event: PaymentEvent):
        """Handle successful payment."""
        try:
            message = self.get_payment_message('payment_success', payment_event.language)
            formatted_amount = self.format_amount(
                payment_event.amount, 
                payment_event.currency, 
                payment_event.language
            )
            
            logger.info(f"Payment success: {formatted_amount} for customer {payment_event.customer_id}")
            
            # Update customer data
            await self._update_customer_payment_status(payment_event.customer_id, 'active')
            
            # Send confirmation (could be email, SMS, etc.)
            await self._send_payment_confirmation(payment_event, message)
            
        except Exception as e:
            logger.error(f"Error handling payment success: {e}")
    
    async def _handle_payment_failure(self, payment_event: PaymentEvent):
        """Handle failed payment."""
        try:
            message = self.get_payment_message('payment_failed', payment_event.language)
            
            logger.warning(f"Payment failed for customer {payment_event.customer_id}")
            
            # Update customer data
            await self._update_customer_payment_status(payment_event.customer_id, 'failed')
            
            # Send failure notification
            await self._send_payment_notification(payment_event, message)
            
        except Exception as e:
            logger.error(f"Error handling payment failure: {e}")
    
    async def _handle_refund(self, payment_event: PaymentEvent):
        """Handle refund."""
        try:
            message = self.get_payment_message('refund_processed', payment_event.language)
            formatted_amount = self.format_amount(
                payment_event.amount, 
                payment_event.currency, 
                payment_event.language
            )
            
            logger.info(f"Refund processed: {formatted_amount} for customer {payment_event.customer_id}")
            
            # Update customer data
            await self._update_customer_payment_status(payment_event.customer_id, 'refunded')
            
            # Send refund confirmation
            await self._send_payment_confirmation(payment_event, message)
            
        except Exception as e:
            logger.error(f"Error handling refund: {e}")
    
    async def _handle_subscription_created(self, payment_event: PaymentEvent):
        """Handle subscription creation."""
        try:
            message = self.get_payment_message('subscription_created', payment_event.language)
            
            logger.info(f"Subscription created for customer {payment_event.customer_id}")
            
            # Update customer subscription status
            await self._update_customer_subscription_status(payment_event.customer_id, 'active')
            
            # Send welcome message
            await self._send_subscription_welcome(payment_event, message)
            
        except Exception as e:
            logger.error(f"Error handling subscription creation: {e}")
    
    async def _handle_subscription_cancelled(self, payment_event: PaymentEvent):
        """Handle subscription cancellation."""
        try:
            message = self.get_payment_message('subscription_cancelled', payment_event.language)
            
            logger.info(f"Subscription cancelled for customer {payment_event.customer_id}")
            
            # Update customer subscription status
            await self._update_customer_subscription_status(payment_event.customer_id, 'cancelled')
            
            # Send cancellation notification
            await self._send_subscription_notification(payment_event, message)
            
        except Exception as e:
            logger.error(f"Error handling subscription cancellation: {e}")
    
    async def _update_customer_payment_status(self, customer_id: str, status: str):
        """Update customer payment status in database."""
        try:
            # This would typically update a database
            # For now, just log the update
            logger.info(f"Updated customer {customer_id} payment status to {status}")
            
        except Exception as e:
            logger.error(f"Error updating customer payment status: {e}")
    
    async def _update_customer_subscription_status(self, customer_id: str, status: str):
        """Update customer subscription status in database."""
        try:
            # This would typically update a database
            # For now, just log the update
            logger.info(f"Updated customer {customer_id} subscription status to {status}")
            
        except Exception as e:
            logger.error(f"Error updating customer subscription status: {e}")
    
    async def _send_payment_confirmation(self, payment_event: PaymentEvent, message: str):
        """Send payment confirmation to customer."""
        try:
            # This would typically send an email, SMS, or push notification
            # For now, just log the confirmation
            formatted_amount = self.format_amount(
                payment_event.amount, 
                payment_event.currency, 
                payment_event.language
            )
            
            logger.info(f"Payment confirmation sent: {message} - {formatted_amount}")
            
        except Exception as e:
            logger.error(f"Error sending payment confirmation: {e}")
    
    async def _send_payment_notification(self, payment_event: PaymentEvent, message: str):
        """Send payment notification to customer."""
        try:
            # This would typically send an email, SMS, or push notification
            # For now, just log the notification
            logger.info(f"Payment notification sent: {message}")
            
        except Exception as e:
            logger.error(f"Error sending payment notification: {e}")
    
    async def _send_subscription_welcome(self, payment_event: PaymentEvent, message: str):
        """Send subscription welcome message."""
        try:
            # This would typically send a welcome email
            # For now, just log the welcome message
            logger.info(f"Subscription welcome sent: {message}")
            
        except Exception as e:
            logger.error(f"Error sending subscription welcome: {e}")
    
    async def _send_subscription_notification(self, payment_event: PaymentEvent, message: str):
        """Send subscription notification."""
        try:
            # This would typically send a notification
            # For now, just log the notification
            logger.info(f"Subscription notification sent: {message}")
            
        except Exception as e:
            logger.error(f"Error sending subscription notification: {e}")


# Initialize payment processor
payment_processor = MultiCurrencyPaymentProcessor()


def verify_webhook_signature(payload: bytes, signature: str) -> bool:
    """Verify webhook signature for security."""
    try:
        if not webhook_secret:
            logger.warning("No webhook secret configured - skipping signature verification")
            return True
        
        # Verify signature
        expected_signature = hmac.new(
            webhook_secret.encode('utf-8'),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(f"whsec_{expected_signature}", signature)
        
    except Exception as e:
        logger.error(f"Error verifying webhook signature: {e}")
        return False


@app.route('/webhook', methods=['POST'])
async def webhook_handler():
    """Handle Stripe webhook events with multi-currency support."""
    try:
        # Get request data
        payload = request.get_data()
        signature = request.headers.get('Stripe-Signature', '')
        
        # Verify webhook signature
        if not verify_webhook_signature(payload, signature):
            logger.error("Invalid webhook signature")
            return jsonify({'error': 'Invalid signature'}), 400
        
        # Parse event
        try:
            event = stripe.Webhook.construct_event(
                payload, signature, webhook_secret
            )
        except ValueError as e:
            logger.error(f"Invalid payload: {e}")
            return jsonify({'error': 'Invalid payload'}), 400
        except stripe.error.SignatureVerificationError as e:
            logger.error(f"Invalid signature: {e}")
            return jsonify({'error': 'Invalid signature'}), 400
        
        # Process the event
        payment_event = await payment_processor.process_payment_event(event)
        
        # Log successful processing
        logger.info(f"Webhook processed successfully: {payment_event.event_type}")
        
        return jsonify({
            'status': 'success',
            'event_id': payment_event.event_id,
            'event_type': payment_event.event_type,
            'message': 'Webhook processed successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'supported_currencies': list(SUPPORTED_CURRENCIES.keys()),
        'supported_languages': list(LANGUAGE_CURRENCIES.keys())
    }), 200


@app.route('/currencies', methods=['GET'])
def get_currencies():
    """Get supported currencies."""
    return jsonify({
        'currencies': SUPPORTED_CURRENCIES,
        'language_currencies': LANGUAGE_CURRENCIES
    }), 200


@app.route('/test-payment', methods=['POST'])
async def test_payment():
    """Test payment endpoint for development."""
    try:
        data = request.get_json()
        language = data.get('language', 'en')
        currency = data.get('currency', LANGUAGE_CURRENCIES.get(language, 'USD'))
        amount = data.get('amount', 1000)  # $10.00
        
        # Create test payment event
        test_event = PaymentEvent(
            event_id='test_event_123',
            event_type='payment_intent.succeeded',
            customer_id='test_customer_123',
            amount=amount / 100,  # Convert from cents
            currency=currency,
            language=language,
            metadata={'test': True, 'language': language},
            timestamp=datetime.utcnow(),
            status='test'
        )
        
        # Process test event
        await payment_processor._handle_payment_success(test_event)
        
        formatted_amount = payment_processor.format_amount(
            test_event.amount, 
            test_event.currency, 
            test_event.language
        )
        
        return jsonify({
            'status': 'success',
            'message': f'Test payment processed: {formatted_amount}',
            'language': language,
            'currency': currency,
            'amount': formatted_amount
        }), 200
        
    except Exception as e:
        logger.error(f"Error in test payment: {e}")
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    # Run the Flask app
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True) 