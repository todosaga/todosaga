FROM python:3.12-slim

# Copy uv from other image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install dependencies
COPY pyproject.toml .
COPY uv.lock .
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy project
COPY ./todosaga /app/todosaga

# Set work directory
WORKDIR /app/todosaga


# Create necessary directories
RUN mkdir -p /app/staticfiles /app/media

# Set permissions
RUN chmod -R 755 /app/staticfiles /app/media 