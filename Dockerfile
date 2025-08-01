FROM python:3.13-rc-slim

# Set Python environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Poetry
RUN pip install --upgrade pip && \
    pip install poetry

# Copy dependency files
COPY pyproject.toml poetry.lock* ./

# Install project dependencies (only main and dev groups)
RUN poetry config virtualenvs.create false && \
    poetry install --no-root --only main,dev

# Copy application code
COPY . .