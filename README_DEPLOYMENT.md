# AutoPilot Ventures - Global Deployment Guide

## 🚀 Overview

This guide provides comprehensive instructions for deploying the AutoPilot Ventures platform globally with 10 AI agents, multi-currency payment processing, and autonomous capabilities.

## 📋 Prerequisites

### Required Services
- **OpenAI API Key** (for AI agents)
- **DeepL API Key** (for translations)
- **Stripe Account** (for payments)
- **Google Cloud Project** (for Cloud Run)
- **Vercel Account** (for edge deployment)
- **GitHub Account** (for CI/CD)

### Infrastructure Requirements
- **Python 3.11+**
- **Docker** (for containerization)
- **Redis** (for caching and message bus)
- **PostgreSQL/SQLite** (for database)

## 🔧 Local Development Setup

### 1. Environment Configuration
```bash
# Clone repository
git clone <repository-url>
cd autopilot-ventures

# Create environment file
cp .env.example .env

# Configure API keys
OPENAI_SECRET_KEY=your_openai_key_here
DEEPL_API_KEY=your_deepl_key_here
STRIPE_SECRET_KEY=your_stripe_secret_key_here
STRIPE_WEBHOOK_SECRET=your_stripe_webhook_secret_here
FERNET_KEY=your_fernet_key_here
```

### 2. Install Dependencies
```bash
# Install Python dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements-dev.txt
```

### 3. Initialize Database
```bash
# Run setup script
python setup.py

# Initialize database
python -c "from database import db_manager; db_manager.init_database()"
```

### 4. Test Local Deployment
```bash
# Test all agents
python test_agents.py

# Test global deployment
python test_global_deployment.py

# Run main application
python main.py
```

## 🐳 Docker Deployment

### 1. Build Docker Image
```bash
# Build production image
docker build -t autopilot-ventures:latest .

# Build with specific target
docker build --target production -t autopilot-ventures:prod .
```

### 2. Run Container
```bash
# Run with environment variables
docker run -d \
  --name autopilot-ventures \
  -p 5000:5000 \
  -e OPENAI_SECRET_KEY=your_key \
  -e DEEPL_API_KEY=your_key \
  -e STRIPE_SECRET_KEY=your_key \
  autopilot-ventures:latest

# Run with docker-compose
docker-compose up -d
```

### 3. Docker Compose Configuration
```yaml
# docker-compose.yml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "5000:5000"
    environment:
      - OPENAI_SECRET_KEY=${OPENAI_SECRET_KEY}
      - DEEPL_API_KEY=${DEEPL_API_KEY}
      - STRIPE_SECRET_KEY=${STRIPE_SECRET_KEY}
    depends_on:
      - redis
      - postgres
  
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
  
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: autopilot_ventures
      POSTGRES_USER: autopilot
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

## ☁️ Google Cloud Run Deployment

### 1. Project Setup
```bash
# Set project ID
export PROJECT_ID=your-project-id
gcloud config set project $PROJECT_ID

# Enable required APIs
gcloud services enable \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  containerregistry.googleapis.com
```

### 2. Build and Deploy
```bash
# Build and push to Container Registry
gcloud builds submit --tag gcr.io/$PROJECT_ID/autopilot-ventures

# Deploy to Cloud Run
gcloud run deploy autopilot-ventures \
  --image gcr.io/$PROJECT_ID/autopilot-ventures \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars="OPENAI_SECRET_KEY=$OPENAI_SECRET_KEY" \
  --set-env-vars="DEEPL_API_KEY=$DEEPL_API_KEY" \
  --set-env-vars="STRIPE_SECRET_KEY=$STRIPE_SECRET_KEY"
```

### 3. Configure Auto-scaling
```yaml
# app.yaml configuration
automatic_scaling:
  target_cpu_utilization: 0.6
  min_instances: 1
  max_instances: 10
  target_throughput_utilization: 0.6
  max_concurrent_requests: 50
```

## ⚡ Vercel Edge Deployment

### 1. Vercel Configuration
```json
{
  "version": 2,
  "name": "autopilot-ventures",
  "builds": [
    {
      "src": "main.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "main.py"
    }
  ],
  "env": {
    "OPENAI_SECRET_KEY": "@openai_secret_key",
    "DEEPL_API_KEY": "@deepl_api_key",
    "STRIPE_SECRET_KEY": "@stripe_secret_key"
  }
}
```

### 2. Deploy to Vercel
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel --prod

# Set environment variables
vercel env add OPENAI_SECRET_KEY
vercel env add DEEPL_API_KEY
vercel env add STRIPE_SECRET_KEY
```

## 🔄 CI/CD Pipeline

### 1. GitHub Actions Setup
```yaml
# .github/workflows/ci-cd.yml
name: AutoPilot Ventures CI/CD

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Run tests
        run: |
          pip install -r requirements.txt
          python test_global_deployment.py
```

### 2. Automated Deployment
```yaml
  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - name: Deploy to Cloud Run
        uses: google-github-actions/deploy-cloudrun@v1
        with:
          service: autopilot-ventures
          image: gcr.io/${{ secrets.PROJECT_ID }}/autopilot-ventures
          region: us-central1
          project_id: ${{ secrets.PROJECT_ID }}
          credentials: ${{ secrets.GCP_SA_KEY }}
```

## 🔒 Security Configuration

### 1. Environment Variables Security
```bash
# Use secrets management
# Google Cloud Secret Manager
gcloud secrets create openai-key --data-file=openai-key.txt
gcloud secrets create deepl-key --data-file=deepl-key.txt

# Access in application
from google.cloud import secretmanager
client = secretmanager.SecretManagerServiceClient()
name = f"projects/{project_id}/secrets/openai-key/versions/latest"
response = client.access_secret_version(request={"name": name})
openai_key = response.payload.data.decode("UTF-8")
```

### 2. Webhook Security
```python
# Verify Stripe webhook signatures
def verify_webhook_signature(payload, signature):
    expected_signature = hmac.new(
        webhook_secret.encode('utf-8'),
        payload,
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(f"whsec_{expected_signature}", signature)
```

### 3. API Rate Limiting
```python
# Implement rate limiting
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)
```

## 🌍 Global Deployment Testing

### 1. Multi-Language Testing
```bash
# Test Arabic business creation
python test_global_deployment.py --language ar

# Test Japanese business creation
python test_global_deployment.py --language ja

# Test all languages
python test_global_deployment.py --all-languages
```

### 2. Multi-Currency Testing
```bash
# Test payment processing
curl -X POST http://localhost:5000/webhook/test-payment \
  -H "Content-Type: application/json" \
  -d '{"language": "ar", "currency": "USD", "amount": 1000}'
```

### 3. Performance Testing
```bash
# Run load tests
locust -f tests/performance/locustfile.py \
  --host=http://localhost:5000 \
  --users=100 \
  --spawn-rate=10 \
  --run-time=5m
```

## 📊 Monitoring and Observability

### 1. Prometheus Metrics
```python
# Custom metrics
from prometheus_client import Counter, Histogram, Gauge

# Agent execution metrics
AGENT_EXECUTION_COUNTER = Counter(
    'agent_executions_total',
    'Total number of agent executions',
    ['agent_type', 'language', 'status']
)

# Response time metrics
AGENT_EXECUTION_DURATION = Histogram(
    'agent_execution_duration_seconds',
    'Agent execution duration in seconds',
    ['agent_type', 'language']
)
```

### 2. Grafana Dashboards
```json
{
  "dashboard": {
    "title": "AutoPilot Ventures Metrics",
    "panels": [
      {
        "title": "Agent Execution Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(agent_executions_total[5m])",
            "legendFormat": "{{agent_type}}"
          }
        ]
      }
    ]
  }
}
```

### 3. Alerting Configuration
```yaml
# monitoring/alerts.yml
groups:
  - name: autopilot-ventures
    rules:
      - alert: HighErrorRate
        expr: rate(agent_executions_total{status="failed"}[5m]) > 0.1
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "High error rate detected"
```

## 🔧 Auto-scaling Configuration

### 1. Horizontal Pod Autoscaler (Kubernetes)
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: autopilot-ventures-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: autopilot-ventures
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

### 2. Cloud Run Auto-scaling
```yaml
# app.yaml
automatic_scaling:
  target_cpu_utilization: 0.6
  min_instances: 1
  max_instances: 10
  target_throughput_utilization: 0.6
  max_concurrent_requests: 50
  min_idle_instances: 1
  max_idle_instances: 3
```

## 🧪 Testing Strategy

### 1. Unit Tests
```bash
# Run unit tests
pytest tests/unit/ -v --cov=.

# Run with coverage
pytest --cov=. --cov-report=html --cov-report=term
```

### 2. Integration Tests
```bash
# Run integration tests
pytest tests/integration/ -v

# Test with external services
pytest tests/integration/ --external-services
```

### 3. End-to-End Tests
```bash
# Run E2E tests
pytest tests/e2e/ -v

# Test business creation workflow
python tests/e2e/test_business_workflow.py
```

## 📈 Performance Optimization

### 1. Database Optimization
```sql
-- Create indexes for performance
CREATE INDEX idx_agents_startup_id ON agents(startup_id);
CREATE INDEX idx_workflows_timestamp ON workflows(created_at);
CREATE INDEX idx_payments_customer_id ON payments(customer_id);
```

### 2. Caching Strategy
```python
# Redis caching
import redis
from functools import wraps

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def cache_result(ttl=300):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
            cached_result = redis_client.get(cache_key)
            
            if cached_result:
                return json.loads(cached_result)
            
            result = await func(*args, **kwargs)
            redis_client.setex(cache_key, ttl, json.dumps(result))
            return result
        return wrapper
    return decorator
```

### 3. Connection Pooling
```python
# Database connection pooling
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=30,
    pool_pre_ping=True,
    pool_recycle=3600
)
```

## 🚨 Troubleshooting

### 1. Common Issues
```bash
# Check application logs
docker logs autopilot-ventures

# Check health endpoint
curl http://localhost:5000/health

# Check database connection
python -c "from database import db_manager; print(db_manager.get_database_stats())"
```

### 2. Performance Issues
```bash
# Monitor resource usage
docker stats autopilot-ventures

# Check slow queries
python -c "from database import db_manager; db_manager.analyze_slow_queries()"
```

### 3. Security Issues
```bash
# Run security audit
bandit -r . -f json -o security-report.json

# Check for vulnerabilities
safety check --json --output vulnerabilities.json
```

## 📚 Additional Resources

- [Google Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Vercel Documentation](https://vercel.com/docs)
- [Stripe Webhook Guide](https://stripe.com/docs/webhooks)
- [Prometheus Monitoring](https://prometheus.io/docs/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)

---

**🎉 Your AutoPilot Ventures platform is now ready for global deployment with comprehensive monitoring, security, and auto-scaling capabilities!** 