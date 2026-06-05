FROM python:3.13-slim

# Disable stdout/stderr buffering
ENV PYTHONUNBUFFERED=1

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

RUN apt-get update && apt-get upgrade -y && rm -rf /var/lib/apt/lists/*

# Copy dependency files
COPY pyproject.toml ./

# Generate requirements.txt and install dependencies
# This allows caching dependencies even without the source code
RUN uv pip compile pyproject.toml -o requirements.txt \
    && uv pip install --system --no-cache -r requirements.txt

# Copy source code and migration files
COPY app/ ./app/
COPY alembic/ ./alembic/
COPY alembic.ini ./
COPY entrypoint.sh ./
RUN chmod +x entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]
