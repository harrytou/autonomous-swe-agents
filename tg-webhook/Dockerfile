FROM python:3.11-slim

# Install git for project initialization
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/* \
    && git config --global user.email "bot@opencode.local" \
    && git config --global user.name "OpenCode Bot"

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY config.py .
COPY webhook.py .
COPY db/ ./db/

# Create data directory structure
RUN mkdir -p /data/db /data/projects

EXPOSE 8000

CMD ["uvicorn", "webhook:app", "--host", "0.0.0.0", "--port", "8000"]
