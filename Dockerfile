# AutoPilot Ventures Platform Dockerfile
# Multi-stage build for optimized production deployment

# Stage 1: Base Python environment
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Development environment
FROM base as development

# Install development dependencies
RUN pip install --no-cache-dir \
    pytest \
    pytest-asyncio \
    pytest-cov \
    black \
    flake8 \
    mypy

# Copy source code
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash app && \
    chown -R app:app /app
USER app

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Development command
CMD ["python", "main.py"]

# Stage 3: Production environment
FROM base as production

# Install production dependencies
RUN pip install --no-cache-dir \
    gunicorn \
    uvicorn[standard]

# Copy source code
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash app && \
    chown -R app:app /app
USER app

# Create necessary directories
RUN mkdir -p /app/logs /app/data /app/uploads

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Production command
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "main:app"]

# Stage 4: Webhook handler
FROM base as webhook

# Install webhook-specific dependencies
RUN pip install --no-cache-dir \
    flask \
    stripe

# Copy webhook handler
COPY webhook_handler.py .

# Create non-root user
RUN useradd --create-home --shell /bin/bash app && \
    chown -R app:app /app
USER app

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Webhook command
CMD ["python", "webhook_handler.py"]

# Stage 5: Monitoring
FROM base as monitoring

# Install monitoring dependencies
RUN pip install --no-cache-dir \
    prometheus_client \
    grafana_api \
    jaeger_client

# Copy monitoring configuration
COPY monitoring/ ./monitoring/

# Create non-root user
RUN useradd --create-home --shell /bin/bash app && \
    chown -R app:app /app
USER app

# Expose monitoring port
EXPOSE 9090

# Monitoring command
CMD ["python", "-m", "prometheus_client", "--port", "9090"]

# Stage 6: Testing
FROM base as testing

# Install testing dependencies
RUN pip install --no-cache-dir \
    pytest \
    pytest-asyncio \
    pytest-cov \
    pytest-mock \
    hypothesis

# Copy source code and tests
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash app && \
    chown -R app:app /app
USER app

# Run tests
CMD ["pytest", "-v", "--cov=.", "--cov-report=html", "--cov-report=term"] 