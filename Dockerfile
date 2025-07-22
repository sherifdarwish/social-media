# Multi-stage Dockerfile for Social Media Agent

# Build stage
FROM python:3.11-slim as builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create and activate virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Production stage
FROM python:3.11-slim as production

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH" \
    PYTHONPATH="/app"

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd -r appuser \
    && useradd -r -g appuser appuser

# Copy virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv

# Create app directory
WORKDIR /app

# Copy application code
COPY src/ ./src/
COPY examples/ ./examples/
COPY scripts/ ./scripts/
COPY README.md LICENSE ./

# Create necessary directories
RUN mkdir -p /app/logs /app/data /app/config \
    && chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import src; print('Health check passed')" || exit 1

# Expose port
EXPOSE 8000

# Default command
CMD ["python", "-m", "src.main"]

# Development stage
FROM production as development

# Switch back to root for development tools installation
USER root

# Install development dependencies
COPY requirements-dev.txt .
RUN pip install -r requirements-dev.txt

# Install additional development tools
RUN apt-get update && apt-get install -y \
    vim \
    htop \
    && rm -rf /var/lib/apt/lists/*

# Copy test files
COPY tests/ ./tests/
COPY pytest.ini .

# Switch back to appuser
USER appuser

# Development command
CMD ["python", "-m", "pytest", "tests/", "-v"]

# Testing stage
FROM development as testing

# Run tests
RUN python -m pytest tests/ -v --cov=src --cov-report=html

# Production-ready stage with minimal footprint
FROM python:3.11-alpine as minimal

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH" \
    PYTHONPATH="/app"

# Install runtime dependencies
RUN apk add --no-cache \
    curl \
    && addgroup -g 1001 -S appuser \
    && adduser -S appuser -G appuser

# Copy virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv

# Create app directory
WORKDIR /app

# Copy only necessary application files
COPY --chown=appuser:appuser src/ ./src/
COPY --chown=appuser:appuser examples/config.example.yaml ./config/
COPY --chown=appuser:appuser README.md LICENSE ./

# Create necessary directories
RUN mkdir -p /app/logs /app/data \
    && chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import src; print('Health check passed')" || exit 1

# Expose port
EXPOSE 8000

# Default command
CMD ["python", "-m", "src.main"]

