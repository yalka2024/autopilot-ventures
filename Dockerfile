# Multi-stage Dockerfile for AutoPilot Ventures - Production Ready
# Stage 1: Base image with common dependencies
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    wget \
    unzip \
    software-properties-common \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd --create-home --shell /bin/bash appuser

# Stage 2: Dependencies installation with caching
FROM base as dependencies

# Set work directory
WORKDIR /app

# Copy requirements files
COPY requirements.txt .

# Install Python dependencies with caching
RUN pip install --upgrade pip setuptools wheel
RUN pip install -r requirements.txt

# Stage 3: Application build
FROM dependencies as builder

# Copy application code
COPY . .

# Install application in development mode
RUN pip install -e .

# Stage 4: Production runtime
FROM base as production

# Set work directory
WORKDIR /app

# Copy Python dependencies from dependencies stage
COPY --from=dependencies /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=dependencies /usr/local/bin /usr/local/bin

# Copy application code from builder stage
COPY --from=builder /app /app

# Copy specific directories that might be needed
COPY --from=builder /app/data /app/data
COPY --from=builder /app/templates /app/templates
COPY --from=builder /app/static /app/static

# Set ownership to non-root user
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Default command
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]

# Stage 5: Final production image with labels
FROM production as final

# Add labels for better container management
LABEL maintainer="AutoPilot Ventures Team"
LABEL version="1.0.0"
LABEL description="AutoPilot Ventures - Multilingual AI Agent Platform"
LABEL org.opencontainers.image.source="https://github.com/autopilot-ventures/platform"

# Copy startup script
COPY scripts/startup.sh /app/startup.sh
RUN chmod +x /app/startup.sh

# Set entrypoint
ENTRYPOINT ["/app/startup.sh"]
