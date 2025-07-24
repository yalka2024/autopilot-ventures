# Multi-stage Dockerfile for AutoPilot Ventures - Multilingual Agent Platform
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
COPY requirements-dev.txt* .

# Install Python dependencies with caching
RUN pip install --upgrade pip setuptools wheel
RUN pip install -r requirements.txt

# Stage 3: Development dependencies (optional)
FROM dependencies as development

# Install development dependencies if requirements-dev.txt exists
RUN if [ -f requirements-dev.txt ]; then pip install -r requirements-dev.txt; fi

# Stage 4: Application build
FROM dependencies as builder

# Copy application code
COPY . .

# Install application in development mode
RUN pip install -e .

# Stage 5: Production runtime
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

# Stage 6: Multilingual agent preparation
FROM production as multilingual-agent

# Install additional language support
RUN apt-get update && apt-get install -y \
    locales \
    language-pack-en \
    language-pack-es \
    language-pack-fr \
    language-pack-de \
    language-pack-it \
    language-pack-pt \
    language-pack-ru \
    language-pack-zh \
    language-pack-ja \
    language-pack-ko \
    && rm -rf /var/lib/apt/lists/*

# Generate locales
RUN locale-gen en_US.UTF-8 && \
    locale-gen es_ES.UTF-8 && \
    locale-gen fr_FR.UTF-8 && \
    locale-gen de_DE.UTF-8 && \
    locale-gen it_IT.UTF-8 && \
    locale-gen pt_BR.UTF-8 && \
    locale-gen ru_RU.UTF-8 && \
    locale-gen zh_CN.UTF-8 && \
    locale-gen ja_JP.UTF-8 && \
    locale-gen ko_KR.UTF-8

# Set default locale
ENV LANG=en_US.UTF-8
ENV LC_ALL=en_US.UTF-8

# Install additional Python packages for multilingual support
RUN pip install --no-cache-dir \
    polyglot \
    langdetect \
    googletrans==4.0.0rc1 \
    sentencepiece \
    sacremoses

# Copy multilingual models and data
COPY --from=builder /app/models /app/models
COPY --from=builder /app/language_data /app/language_data

# Stage 7: Testing environment
FROM development as testing

# Install testing dependencies
RUN pip install --no-cache-dir \
    pytest \
    pytest-asyncio \
    pytest-cov \
    pytest-mock \
    hypothesis \
    coverage

# Copy test files
COPY tests/ /app/tests/
COPY pytest.ini* /app/

# Set test environment
ENV PYTHONPATH=/app
ENV TESTING=1

# Default test command
CMD ["pytest", "-v", "--cov=app", "--cov-report=html"]

# Stage 8: Final production image
FROM multilingual-agent as final

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
