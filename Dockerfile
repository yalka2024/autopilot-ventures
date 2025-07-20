# AutoPilot Ventures Dockerfile
# Multi-stage build for optimized production image

# Base stage
FROM python:3.11-slim AS base

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    wget \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Development stage
FROM base AS development

# Install development dependencies
RUN pip install --no-cache-dir \
    pytest \
    pytest-asyncio \
    pytest-mock \
    black \
    flake8 \
    mypy

# Copy source code
COPY . .

# Create necessary directories
RUN mkdir -p data logs startups templates uploads exports backups

# Set permissions
RUN chmod +x main.py

# Expose ports
EXPOSE 8501 9090

# Development command
CMD ["python", "main.py", "--start-autonomous", "--autonomous-mode", "semi"]

# Production stage
FROM base AS production

# Copy source code
COPY . .

# Create necessary directories
RUN mkdir -p data logs startups templates uploads exports backups

# Set permissions
RUN chmod +x main.py

# Create non-root user
RUN useradd --create-home --shell /bin/bash autopilot && \
    chown -R autopilot:autopilot /app

USER autopilot

# Expose ports
EXPOSE 8501 9090

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8501/ || exit 1

# Production command
CMD ["python", "main.py", "--start-autonomous", "--autonomous-mode", "semi"]

# Testing stage
FROM development AS testing

# Run tests
RUN python -m pytest tests/ -v

# Default to development
FROM development 