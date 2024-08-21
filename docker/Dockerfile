# Base image for dependency installation
FROM python:3.12.1-slim-bullseye AS build

# Update and install dependencies for building
RUN apt-get update -y && \
    apt-get upgrade -y && \
    apt-get install -y \
        git \
        build-essential \
        libpq-dev \
        gcc && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Upgrade pip, setuptools, and wheel
RUN python -m ensurepip --upgrade
RUN python -m pip install --upgrade pip setuptools wheel

# Install Poetry
RUN python -m pip install poetry

# Create and set working directory
RUN mkdir -p /usr/crypto_bot/
WORKDIR /usr/crypto_bot/

# Copy dependency files
COPY pyproject.toml poetry.lock ./

# Configure Poetry to not create virtualenvs
RUN poetry config virtualenvs.create false

# Install all dependencies without PEP 517 for psycopg2
RUN poetry install --no-root
RUN pip install --no-binary :all: psycopg2

# Image to run the application
FROM build AS main

# Ensure /usr/crypto_bot directory exists and has appropriate permissions
RUN mkdir -p /usr/crypto_bot/ && chmod a+rw /usr/crypto_bot
WORKDIR /usr/crypto_bot/

# Set environment variables
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONPATH="/usr/crypto_bot"

# Copy application code to the container
COPY . /usr/crypto_bot

# Command to run your application entry point. Example:
CMD ["python", "your_entry_point.py"]
