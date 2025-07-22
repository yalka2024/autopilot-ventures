"""Payment processing and revenue automation system."""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import stripe
from decimal import Decimal

from config import config
from utils import generate_id, log, security_utils

logger = logging.getLogger(__name__)

# Initialize Stripe
stripe.api_key = config.stripe.secret_key


class PaymentStatus(Enum):
    """Payment status enumeration."""
    
    PENDING = "pending"
    PROCESSING = "processing"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class SubscriptionStatus(Enum):
    """Subscription status enumeration."""
    
    ACTIVE = "active"
    PAST_DUE = "past_due"
    CANCELED = "canceled"
    UNPAID = "unpaid"
    TRIAL = "trial"


@dataclass
class PaymentIntent:
    """Payment intent data structure."""
    
    id: str
    amount: int  # Amount in cents
    currency: str
    status: PaymentStatus
    customer_id: str
    description: str
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime


@dataclass
class Customer:
    """Customer data structure."""
    
    id: str
    email: str
    name: str
    phone: Optional[str]
    metadata: Dict[str, Any]
    created_at: datetime
    total_spent: int = 0  # Total spent in cents
    subscription_count: int = 0


@dataclass
class Subscription:
    """Subscription data structure."""
    
    id: str
    customer_id: str
    plan_id: str
    status: SubscriptionStatus
    current_period_start: datetime
    current_period_end: datetime
    amount: int  # Amount in cents
    currency: str
    metadata: Dict[str, Any]
    created_at: datetime


@dataclass
class Product:
    """Product data structure."""
    
    id: str
    name: str
    description: str
    price: int  # Price in cents
    currency: str
    interval: str  # monthly, yearly, one-time
    features: List[str]
    metadata: Dict[str, Any]
    active: bool = True


class PaymentProcessor:
    """Payment processing system with Stripe integration."""
    
    def __init__(self):
        self.customers: Dict[str, Customer] = {}
        self.subscriptions: Dict[str, Subscription] = {}
        self.products: Dict[str, Product] = {}
        self.payment_intents: Dict[str, PaymentIntent] = {}
        
        # Initialize default products
        self._initialize_default_products()
        
        logger.info("Payment processor initialized")
    
    def _initialize_default_products(self):
        """Initialize default product offerings."""
        default_products = [
            {
                'id': 'basic_plan',
                'name': 'Basic Plan',
                'description': 'Essential features for startups',
                'price': 2900,  # $29.00
                'currency': 'usd',
                'interval': 'monthly',
                'features': ['Basic analytics', 'Email support', '5 projects']
            },
            {
                'id': 'pro_plan',
                'name': 'Pro Plan',
                'description': 'Advanced features for growing businesses',
                'price': 7900,  # $79.00
                'currency': 'usd',
                'interval': 'monthly',
                'features': ['Advanced analytics', 'Priority support', 'Unlimited projects', 'API access']
            },
            {
                'id': 'enterprise_plan',
                'name': 'Enterprise Plan',
                'description': 'Full-featured solution for large organizations',
                'price': 19900,  # $199.00
                'currency': 'usd',
                'interval': 'monthly',
                'features': ['Custom analytics', 'Dedicated support', 'Unlimited everything', 'Custom integrations']
            }
        ]
        
        for product_data in default_products:
            product = Product(
                id=product_data['id'],
                name=product_data['name'],
                description=product_data['description'],
                price=product_data['price'],
                currency=product_data['currency'],
                interval=product_data['interval'],
                features=product_data['features'],
                metadata={},
                active=True
            )
            self.products[product.id] = product
    
    async def create_customer(
        self,
        email: str,
        name: str,
        phone: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Customer:
        """Create a new customer."""
        try:
            # Create customer in Stripe
            stripe_customer = stripe.Customer.create(
                email=email,
                name=name,
                phone=phone,
                metadata=metadata or {}
            )
            
            # Create local customer record
            customer = Customer(
                id=stripe_customer.id,
                email=email,
                name=name,
                phone=phone,
                metadata=metadata or {},
                created_at=datetime.utcnow()
            )
            
            self.customers[customer.id] = customer
            logger.info(f"Customer created: {customer.id} ({email})")
            return customer
            
        except stripe.error.StripeError as e:
            logger.error(f"Failed to create customer: {e}")
            raise
    
    async def create_payment_intent(
        self,
        customer_id: str,
        amount: int,
        currency: str = 'usd',
        description: str = '',
        metadata: Optional[Dict[str, Any]] = None
    ) -> PaymentIntent:
        """Create a payment intent."""
        try:
            # Create payment intent in Stripe
            stripe_intent = stripe.PaymentIntent.create(
                amount=amount,
                currency=currency,
                customer=customer_id,
                description=description,
                metadata=metadata or {},
                automatic_payment_methods={'enabled': True}
            )
            
            # Create local payment intent record
            payment_intent = PaymentIntent(
                id=stripe_intent.id,
                amount=amount,
                currency=currency,
                status=PaymentStatus(stripe_intent.status),
                customer_id=customer_id,
                description=description,
                metadata=metadata or {},
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            self.payment_intents[payment_intent.id] = payment_intent
            logger.info(f"Payment intent created: {payment_intent.id} for {amount/100:.2f} {currency}")
            return payment_intent
            
        except stripe.error.StripeError as e:
            logger.error(f"Failed to create payment intent: {e}")
            raise
    
    async def create_subscription(
        self,
        customer_id: str,
        plan_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Subscription:
        """Create a subscription for a customer."""
        try:
            product = self.products.get(plan_id)
            if not product:
                raise ValueError(f"Product {plan_id} not found")
            
            # Create price in Stripe if it doesn't exist
            price = stripe.Price.create(
                unit_amount=product.price,
                currency=product.currency,
                recurring={'interval': product.interval},
                product_data={
                    'name': product.name,
                    'description': product.description
                }
            )
            
            # Create subscription in Stripe
            stripe_subscription = stripe.Subscription.create(
                customer=customer_id,
                items=[{'price': price.id}],
                metadata=metadata or {}
            )
            
            # Create local subscription record
            subscription = Subscription(
                id=stripe_subscription.id,
                customer_id=customer_id,
                plan_id=plan_id,
                status=SubscriptionStatus(stripe_subscription.status),
                current_period_start=datetime.fromtimestamp(stripe_subscription.current_period_start),
                current_period_end=datetime.fromtimestamp(stripe_subscription.current_period_end),
                amount=product.price,
                currency=product.currency,
                metadata=metadata or {},
                created_at=datetime.utcnow()
            )
            
            self.subscriptions[subscription.id] = subscription
            
            # Update customer subscription count
            if customer_id in self.customers:
                self.customers[customer_id].subscription_count += 1
            
            logger.info(f"Subscription created: {subscription.id} for customer {customer_id}")
            return subscription
            
        except stripe.error.StripeError as e:
            logger.error(f"Failed to create subscription: {e}")
            raise
    
    async def process_webhook(self, payload: str, sig_header: str) -> Dict[str, Any]:
        """Process Stripe webhook events."""
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, config.stripe.webhook_secret
            )
            
            # Handle different event types
            if event['type'] == 'payment_intent.succeeded':
                await self._handle_payment_success(event['data']['object'])
            elif event['type'] == 'payment_intent.payment_failed':
                await self._handle_payment_failure(event['data']['object'])
            elif event['type'] == 'customer.subscription.created':
                await self._handle_subscription_created(event['data']['object'])
            elif event['type'] == 'customer.subscription.updated':
                await self._handle_subscription_updated(event['data']['object'])
            elif event['type'] == 'customer.subscription.deleted':
                await self._handle_subscription_cancelled(event['data']['object'])
            
            return {'status': 'success', 'event_type': event['type']}
            
        except ValueError as e:
            logger.error(f"Invalid payload: {e}")
            raise
        except stripe.error.SignatureVerificationError as e:
            logger.error(f"Invalid signature: {e}")
            raise
    
    async def _handle_payment_success(self, payment_intent_data: Dict[str, Any]):
        """Handle successful payment."""
        payment_intent_id = payment_intent_data['id']
        
        if payment_intent_id in self.payment_intents:
            self.payment_intents[payment_intent_id].status = PaymentStatus.SUCCEEDED
            self.payment_intents[payment_intent_id].updated_at = datetime.utcnow()
            
            # Update customer total spent
            customer_id = payment_intent_data['customer']
            if customer_id in self.customers:
                self.customers[customer_id].total_spent += payment_intent_data['amount']
            
            logger.info(f"Payment succeeded: {payment_intent_id}")
    
    async def _handle_payment_failure(self, payment_intent_data: Dict[str, Any]):
        """Handle failed payment."""
        payment_intent_id = payment_intent_data['id']
        
        if payment_intent_id in self.payment_intents:
            self.payment_intents[payment_intent_id].status = PaymentStatus.FAILED
            self.payment_intents[payment_intent_id].updated_at = datetime.utcnow()
            
            logger.warning(f"Payment failed: {payment_intent_id}")
    
    async def _handle_subscription_created(self, subscription_data: Dict[str, Any]):
        """Handle subscription creation."""
        subscription_id = subscription_data['id']
        
        if subscription_id in self.subscriptions:
            self.subscriptions[subscription_id].status = SubscriptionStatus(subscription_data['status'])
            self.subscriptions[subscription_id].current_period_start = datetime.fromtimestamp(subscription_data['current_period_start'])
            self.subscriptions[subscription_id].current_period_end = datetime.fromtimestamp(subscription_data['current_period_end'])
            
            logger.info(f"Subscription created: {subscription_id}")
    
    async def _handle_subscription_updated(self, subscription_data: Dict[str, Any]):
        """Handle subscription updates."""
        subscription_id = subscription_data['id']
        
        if subscription_id in self.subscriptions:
            self.subscriptions[subscription_id].status = SubscriptionStatus(subscription_data['status'])
            self.subscriptions[subscription_id].current_period_start = datetime.fromtimestamp(subscription_data['current_period_start'])
            self.subscriptions[subscription_id].current_period_end = datetime.fromtimestamp(subscription_data['current_period_end'])
            
            logger.info(f"Subscription updated: {subscription_id}")
    
    async def _handle_subscription_cancelled(self, subscription_data: Dict[str, Any]):
        """Handle subscription cancellation."""
        subscription_id = subscription_data['id']
        
        if subscription_id in self.subscriptions:
            self.subscriptions[subscription_id].status = SubscriptionStatus.CANCELED
            
            logger.info(f"Subscription cancelled: {subscription_id}")
    
    def get_customer(self, customer_id: str) -> Optional[Customer]:
        """Get customer by ID."""
        return self.customers.get(customer_id)
    
    def get_subscription(self, subscription_id: str) -> Optional[Subscription]:
        """Get subscription by ID."""
        return self.subscriptions.get(subscription_id)
    
    def get_product(self, product_id: str) -> Optional[Product]:
        """Get product by ID."""
        return self.products.get(product_id)
    
    def get_monthly_revenue(self) -> Dict[str, float]:
        """Calculate monthly revenue."""
        current_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        monthly_revenue = 0.0
        active_subscriptions = 0
        
        for subscription in self.subscriptions.values():
            if (subscription.status == SubscriptionStatus.ACTIVE and 
                subscription.current_period_start >= current_month):
                monthly_revenue += subscription.amount / 100  # Convert cents to dollars
                active_subscriptions += 1
        
        return {
            'monthly_revenue': monthly_revenue,
            'active_subscriptions': active_subscriptions,
            'currency': 'USD'
        }
    
    def get_customer_metrics(self) -> Dict[str, Any]:
        """Get customer metrics."""
        total_customers = len(self.customers)
        total_revenue = sum(customer.total_spent for customer in self.customers.values()) / 100
        
        return {
            'total_customers': total_customers,
            'total_revenue': total_revenue,
            'average_revenue_per_customer': total_revenue / total_customers if total_customers > 0 else 0,
            'currency': 'USD'
        }


class MarketingFunnel:
    """Automated marketing funnel system."""
    
    def __init__(self, payment_processor: PaymentProcessor):
        self.payment_processor = payment_processor
        self.funnel_stages = {
            'awareness': [],
            'interest': [],
            'consideration': [],
            'intent': [],
            'purchase': [],
            'retention': []
        }
        self.conversion_rates = {
            'awareness_to_interest': 0.15,
            'interest_to_consideration': 0.25,
            'consideration_to_intent': 0.40,
            'intent_to_purchase': 0.60,
            'purchase_to_retention': 0.80
        }
    
    async def track_lead(self, email: str, source: str, stage: str = 'awareness'):
        """Track a new lead in the funnel."""
        if stage in self.funnel_stages:
            self.funnel_stages[stage].append({
                'email': email,
                'source': source,
                'stage': stage,
                'timestamp': datetime.utcnow(),
                'converted': False
            })
            
            logger.info(f"Lead tracked: {email} at stage {stage} from {source}")
    
    async def advance_lead(self, email: str, new_stage: str):
        """Advance a lead to the next stage."""
        for stage, leads in self.funnel_stages.items():
            for lead in leads:
                if lead['email'] == email and not lead['converted']:
                    lead['stage'] = new_stage
                    lead['timestamp'] = datetime.utcnow()
                    
                    if new_stage == 'purchase':
                        lead['converted'] = True
                    
                    logger.info(f"Lead advanced: {email} to {new_stage}")
                    return
        
        logger.warning(f"Lead not found: {email}")
    
    def get_funnel_metrics(self) -> Dict[str, Any]:
        """Get funnel conversion metrics."""
        metrics = {}
        
        for stage, leads in self.funnel_stages.items():
            total_leads = len(leads)
            converted_leads = len([lead for lead in leads if lead['converted']])
            
            metrics[stage] = {
                'total_leads': total_leads,
                'converted_leads': converted_leads,
                'conversion_rate': converted_leads / total_leads if total_leads > 0 else 0
            }
        
        return metrics


# Global payment processor instance
_payment_processor: Optional[PaymentProcessor] = None


def get_payment_processor() -> PaymentProcessor:
    """Get or create payment processor instance."""
    global _payment_processor
    if _payment_processor is None:
        _payment_processor = PaymentProcessor()
    return _payment_processor


def get_marketing_funnel() -> MarketingFunnel:
    """Get or create marketing funnel instance."""
    payment_processor = get_payment_processor()
    return MarketingFunnel(payment_processor) 