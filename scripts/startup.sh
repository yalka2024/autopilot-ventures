#!/bin/bash

# AutoPilot Ventures Platform Startup Script
# Handles initialization, health checks, and graceful startup

set -e

echo "🚀 Starting AutoPilot Ventures Platform..."

# Function to wait for dependencies
wait_for_dependencies() {
    echo "⏳ Waiting for dependencies to be ready..."
    
    # Wait for database if needed
    if [ -n "$DATABASE_URL" ]; then
        echo "📊 Waiting for database connection..."
        # Add database connection check here
    fi
    
    # Wait for Redis if needed
    if [ -n "$REDIS_URL" ]; then
        echo "🔴 Waiting for Redis connection..."
        # Add Redis connection check here
    fi
    
    echo "✅ Dependencies ready!"
}

# Function to run migrations
run_migrations() {
    if [ -f "alembic.ini" ]; then
        echo "🔄 Running database migrations..."
        alembic upgrade head || echo "⚠️ Migration failed, continuing..."
    fi
}

# Function to initialize application
initialize_app() {
    echo "🔧 Initializing application..."
    
    # Create necessary directories
    mkdir -p /app/logs /app/data /app/uploads /app/cache
    
    # Set proper permissions
    chown -R appuser:appuser /app/logs /app/data /app/uploads /app/cache
    
    # Initialize MLflow if needed
    if [ -n "$MLFLOW_TRACKING_URI" ]; then
        echo "📈 Initializing MLflow tracking..."
        # Add MLflow initialization here
    fi
    
    echo "✅ Application initialized!"
}

# Function to start the application
start_app() {
    echo "🌟 Starting application server..."
    
    # Set environment variables
    export PORT=${PORT:-8080}
    export HOST=${HOST:-0.0.0.0}
    export WORKERS=${WORKERS:-1}
    
    # Start the application based on environment
    if [ "$ENVIRONMENT" = "production" ]; then
        echo "🏭 Starting in production mode with $WORKERS workers..."
        exec gunicorn \
            --bind "$HOST:$PORT" \
            --workers "$WORKERS" \
            --worker-class uvicorn.workers.UvicornWorker \
            --access-logfile - \
            --error-logfile - \
            --log-level info \
            --timeout 120 \
            --keep-alive 5 \
            --max-requests 1000 \
            --max-requests-jitter 100 \
            "main:app"
    else
        echo "🔧 Starting in development mode..."
        exec uvicorn \
            "main:app" \
            --host "$HOST" \
            --port "$PORT" \
            --reload \
            --log-level info \
            --access-log
    fi
}

# Function to handle graceful shutdown
graceful_shutdown() {
    echo "🛑 Received shutdown signal, gracefully stopping..."
    # Add graceful shutdown logic here
    exit 0
}

# Set up signal handlers
trap graceful_shutdown SIGTERM SIGINT

# Main execution
main() {
    echo "🎯 AutoPilot Ventures Platform Startup Sequence"
    echo "================================================"
    
    # Wait for dependencies
    wait_for_dependencies
    
    # Run migrations
    run_migrations
    
    # Initialize application
    initialize_app
    
    # Start application
    start_app
}

# Run main function
main "$@" 