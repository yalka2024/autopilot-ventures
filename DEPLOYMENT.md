# AutoPilot Ventures Platform - Deployment Guide

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Environment Setup](#environment-setup)
4. [Security Configuration](#security-configuration)
5. [Database Setup](#database-setup)
6. [Deployment Options](#deployment-options)
7. [Monitoring & Alerting](#monitoring--alerting)
8. [Scaling & Performance](#scaling--performance)
9. [Troubleshooting](#troubleshooting)
10. [Maintenance](#maintenance)

## Overview

AutoPilot Ventures Platform v2.0.0 is a comprehensive AI-powered startup automation system featuring:

- **10 AI Agents**: Complete startup lifecycle management
- **Enhanced Security**: Encryption, content safety, secrets management
- **Multi-cloud Support**: AWS, Azure, and local deployment
- **Monitoring & Alerting**: Prometheus metrics, budget alerts
- **Multilingual Support**: 10 languages with cultural context
- **Production Ready**: Rate limiting, error handling, logging

## Prerequisites

### System Requirements

- **Python**: 3.9+ (recommended 3.11+)
- **Memory**: 4GB RAM minimum, 8GB recommended
- **Storage**: 10GB available space
- **Network**: Internet access for API calls

### Software Dependencies

```bash
# Core dependencies
pip install -r requirements.txt

# Development dependencies
pip install black flake8 bandit pytest pytest-asyncio
```

### API Keys Required

- **OpenAI API Key**: For AI agent functionality
- **SerpAPI Key**: For market research (optional)
- **SMTP Credentials**: For email alerts (optional)
- **Slack Webhook**: For Slack alerts (optional)

## Environment Setup

### 1. Clone Repository

```bash
git clone <repository-url>
cd autopilot-ventures
```

### 2. Environment Variables

Create `.env` file:

```bash
# Core Configuration
OPENAI_SECRET_KEY=your_openai_api_key_here
SERPAPI_KEY=your_serpapi_key_here

# Security
FERNET_KEY=your_fernet_key_here
SECRETS_MANAGER=env  # Options: env, aws, azure

# Database
DATABASE_URL=sqlite:///autopilot_ventures.db
# For PostgreSQL: postgresql://user:pass@localhost/autopilot

# Monitoring
PROMETHEUS_PORT=9090
ALERT_EMAIL=alerts@yourcompany.com
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...

# SMTP Configuration (for email alerts)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password

# Cloud Provider Configuration
AWS_REGION=us-east-1
AZURE_KEY_VAULT_URL=https://your-vault.vault.azure.net/
```

### 3. Generate Fernet Key

```bash
python generate_fernet_key.py
```

## Security Configuration

### 1. Secrets Management

#### Environment Variables (Default)
```bash
export OPENAI_SECRET_KEY="sk-your-key-here"
export FERNET_KEY="your-base64-encoded-key"
```

#### AWS Secrets Manager
```bash
# Install AWS CLI and configure credentials
aws configure

# Store secrets
aws secretsmanager create-secret \
    --name "autopilot/openai-key" \
    --secret-string "sk-your-key-here"

aws secretsmanager create-secret \
    --name "autopilot/fernet-key" \
    --secret-string "your-base64-encoded-key"
```

#### Azure Key Vault
```bash
# Install Azure CLI and login
az login

# Create key vault
az keyvault create --name your-vault --resource-group your-rg --location eastus

# Store secrets
az keyvault secret set --vault-name your-vault --name "openai-key" --value "sk-your-key-here"
az keyvault secret set --vault-name your-vault --name "fernet-key" --value "your-base64-encoded-key"
```

### 2. Content Safety Configuration

```python
# In config.py
content_safety_threshold = 0.7  # Adjust based on requirements
allowed_domains = ['yourdomain.com']
blacklisted_domains = ['malicious.com', 'spam.com']
```

### 3. Rate Limiting

```python
# Default: 100 API calls per minute
# Adjust in config.py
rate_limit_per_minute = 100
```

## Database Setup

### 1. SQLite (Development)

```bash
# Automatic setup - database will be created on first run
python main.py --health-check
```

### 2. PostgreSQL (Production)

```bash
# Install PostgreSQL
sudo apt-get install postgresql postgresql-contrib

# Create database
sudo -u postgres createdb autopilot_ventures

# Update DATABASE_URL in .env
DATABASE_URL=postgresql://username:password@localhost/autopilot_ventures
```

### 3. Database Migration

```bash
# Run database initialization
python -c "from database import db_manager; print('Database initialized')"
```

## Deployment Options

### 1. Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run health check
python main.py --health-check

# Run multilingual demo
python main.py --multilingual-demo es

# Create startup
python main.py --create-startup "My Startup" "Description" "Technology"
```

### 2. Docker Deployment

#### Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose ports
EXPOSE 8000 9090

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python main.py --health-check

# Run application
CMD ["python", "main.py"]
```

#### Docker Compose
```yaml
version: '3.8'

services:
  autopilot:
    build: .
    ports:
      - "8000:8000"
      - "9090:9090"
    environment:
      - OPENAI_SECRET_KEY=${OPENAI_SECRET_KEY}
      - FERNET_KEY=${FERNET_KEY}
      - DATABASE_URL=${DATABASE_URL}
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    restart: unless-stopped

  prometheus:
    image: prom/prometheus
    ports:
      - "9091:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'

  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana-storage:/var/lib/grafana

volumes:
  grafana-storage:
```

### 3. Kubernetes Deployment

#### Namespace
```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: autopilot-ventures
```

#### ConfigMap
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: autopilot-config
  namespace: autopilot-ventures
data:
  DATABASE_URL: "postgresql://autopilot:password@postgres-service:5432/autopilot"
  PROMETHEUS_PORT: "9090"
  SECRETS_MANAGER: "aws"
```

#### Secret
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: autopilot-secrets
  namespace: autopilot-ventures
type: Opaque
data:
  OPENAI_SECRET_KEY: <base64-encoded-key>
  FERNET_KEY: <base64-encoded-key>
```

#### Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: autopilot-ventures
  namespace: autopilot-ventures
spec:
  replicas: 3
  selector:
    matchLabels:
      app: autopilot-ventures
  template:
    metadata:
      labels:
        app: autopilot-ventures
    spec:
      containers:
      - name: autopilot
        image: autopilot-ventures:latest
        ports:
        - containerPort: 8000
        - containerPort: 9090
        envFrom:
        - configMapRef:
            name: autopilot-config
        - secretRef:
            name: autopilot-secrets
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
```

#### Service
```yaml
apiVersion: v1
kind: Service
metadata:
  name: autopilot-service
  namespace: autopilot-ventures
spec:
  selector:
    app: autopilot-ventures
  ports:
  - name: http
    port: 8000
    targetPort: 8000
  - name: metrics
    port: 9090
    targetPort: 9090
  type: ClusterIP
```

### 4. AWS Deployment

#### ECS Task Definition
```json
{
  "family": "autopilot-ventures",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "executionRoleArn": "arn:aws:iam::account:role/ecsTaskExecutionRole",
  "taskRoleArn": "arn:aws:iam::account:role/autopilot-task-role",
  "containerDefinitions": [
    {
      "name": "autopilot",
      "image": "account.dkr.ecr.region.amazonaws.com/autopilot:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        },
        {
          "containerPort": 9090,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "SECRETS_MANAGER",
          "value": "aws"
        }
      ],
      "secrets": [
        {
          "name": "OPENAI_SECRET_KEY",
          "valueFrom": "arn:aws:secretsmanager:region:account:secret:autopilot/openai-key"
        },
        {
          "name": "FERNET_KEY",
          "valueFrom": "arn:aws:secretsmanager:region:account:secret:autopilot/fernet-key"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/autopilot-ventures",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

### 5. Azure Deployment

#### Azure Container Instances
```bash
# Create resource group
az group create --name autopilot-rg --location eastus

# Create container registry
az acr create --resource-group autopilot-rg --name autopilotregistry --sku Basic

# Build and push image
az acr build --registry autopilotregistry --image autopilot:latest .

# Deploy container instance
az container create \
  --resource-group autopilot-rg \
  --name autopilot-container \
  --image autopilotregistry.azurecr.io/autopilot:latest \
  --dns-name-label autopilot-app \
  --ports 8000 9090 \
  --environment-variables \
    SECRETS_MANAGER=azure \
    AZURE_KEY_VAULT_URL=https://your-vault.vault.azure.net/ \
  --registry-login-server autopilotregistry.azurecr.io \
  --registry-username $ACR_USERNAME \
  --registry-password $ACR_PASSWORD
```

## Monitoring & Alerting

### 1. Prometheus Configuration

Create `prometheus.yml`:

```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'autopilot-ventures'
    static_configs:
      - targets: ['localhost:9090']
    metrics_path: /metrics
    scrape_interval: 5s

  - job_name: 'node-exporter'
    static_configs:
      - targets: ['localhost:9100']
```

### 2. Grafana Dashboards

Import the following dashboards:

- **Agent Performance**: Monitor agent execution times and success rates
- **Budget Tracking**: Track spending and budget utilization
- **System Health**: Overall platform health metrics
- **API Usage**: Monitor API call patterns and errors

### 3. Alert Rules

Create `alerts.yml`:

```yaml
groups:
  - name: autopilot_alerts
    rules:
      - alert: HighBudgetUsage
        expr: budget_usage_dollars / 500 > 0.8
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Budget usage is high"
          description: "Budget usage is {{ $value }}% of total budget"

      - alert: AgentFailureRate
        expr: rate(agent_executions_total{status="failure"}[5m]) > 0.1
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "High agent failure rate"
          description: "Agent failure rate is {{ $value }} failures per second"

      - alert: APIRateLimit
        expr: rate(api_calls_total[1m]) > 100
        for: 1m
        labels:
          severity: warning
        annotations:
          summary: "API rate limit approaching"
          description: "API calls per minute: {{ $value }}"
```

### 4. Logging Configuration

```python
# Configure structured logging
import structlog

structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)
```

## Scaling & Performance

### 1. Horizontal Scaling

```bash
# Kubernetes
kubectl scale deployment autopilot-ventures --replicas=5

# Docker Swarm
docker service scale autopilot-ventures=5

# ECS
aws ecs update-service --cluster autopilot-cluster --service autopilot-service --desired-count 5
```

### 2. Load Balancing

```yaml
# Nginx configuration
upstream autopilot_backend {
    least_conn;
    server autopilot-1:8000;
    server autopilot-2:8000;
    server autopilot-3:8000;
}

server {
    listen 80;
    server_name autopilot.yourdomain.com;

    location / {
        proxy_pass http://autopilot_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /metrics {
        proxy_pass http://autopilot_backend;
        proxy_set_header Host $host;
    }
}
```

### 3. Caching Strategy

```python
# Redis caching for agent results
import redis

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def cache_agent_result(agent_type, input_data, result):
    cache_key = f"agent:{agent_type}:{hash(str(input_data))}"
    redis_client.setex(cache_key, 3600, json.dumps(result))  # 1 hour TTL

def get_cached_result(agent_type, input_data):
    cache_key = f"agent:{agent_type}:{hash(str(input_data))}"
    cached = redis_client.get(cache_key)
    return json.loads(cached) if cached else None
```

## Troubleshooting

### 1. Common Issues

#### Health Check Failures
```bash
# Check configuration
python main.py --health-check

# Verify environment variables
echo $OPENAI_SECRET_KEY
echo $FERNET_KEY

# Check database connection
python -c "from database import db_manager; print(db_manager.get_database_stats())"
```

#### Agent Execution Failures
```bash
# Check agent logs
tail -f logs/agent_execution.log

# Test individual agent
python main.py --run-agent niche_research config.json

# Verify API keys
curl -H "Authorization: Bearer $OPENAI_SECRET_KEY" https://api.openai.com/v1/models
```

#### Budget Issues
```bash
# Check budget status
python -c "from utils import budget_manager; print(f'Remaining: {budget_manager.get_remaining_budget()}')"

# Reset budget (development only)
python -c "from utils import budget_manager; budget_manager.add_funds(500.0)"
```

### 2. Performance Issues

#### High Memory Usage
```bash
# Monitor memory usage
ps aux | grep python
free -h

# Check for memory leaks
python -m memory_profiler main.py
```

#### Slow Agent Execution
```bash
# Profile agent performance
python -c "import cProfile; cProfile.run('import agents')"

# Check API response times
curl -w "@curl-format.txt" -o /dev/null -s "https://api.openai.com/v1/chat/completions"
```

### 3. Security Issues

#### Encryption Failures
```bash
# Test encryption
python -c "from utils import security_utils; print(security_utils.encrypt_data('test'))"

# Regenerate Fernet key
python generate_fernet_key.py
```

#### Content Safety Issues
```bash
# Test content safety
python -c "from utils import security_utils; print(security_utils.check_content_safety('test content'))"
```

## Maintenance

### 1. Regular Tasks

#### Daily
- Monitor budget usage and alerts
- Check agent performance metrics
- Review error logs

#### Weekly
- Update dependencies
- Backup database
- Review security logs
- Analyze performance trends

#### Monthly
- Update API keys
- Review and rotate secrets
- Performance optimization
- Security audit

### 2. Backup Strategy

```bash
# Database backup
sqlite3 autopilot_ventures.db ".backup backup_$(date +%Y%m%d).db"

# PostgreSQL backup
pg_dump autopilot_ventures > backup_$(date +%Y%m%d).sql

# Configuration backup
tar -czf config_backup_$(date +%Y%m%d).tar.gz .env config.py
```

### 3. Updates

```bash
# Update dependencies
pip install -r requirements.txt --upgrade

# Update application
git pull origin main
python main.py --health-check

# Rollback if needed
git checkout previous-version
python main.py --health-check
```

### 4. Monitoring Maintenance

```bash
# Check Prometheus targets
curl http://localhost:9090/api/v1/targets

# Restart monitoring services
docker-compose restart prometheus grafana

# Check alert rules
curl http://localhost:9090/api/v1/rules
```

---

## Support

For additional support:

1. **Documentation**: Check the README.md and inline code comments
2. **Issues**: Report bugs and feature requests via GitHub Issues
3. **Community**: Join our Discord/Slack for community support
4. **Enterprise**: Contact us for enterprise support and custom deployments

## License

This project is licensed under the MIT License - see the LICENSE file for details. 