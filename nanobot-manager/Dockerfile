FROM python:3.12-slim

WORKDIR /app

# Install SSH client for host-based execution and SSH key generation
RUN apt-get update && apt-get install -y --no-install-recommends openssh-client && rm -rf /var/lib/apt/lists/*

# Create users for common UIDs (1000 and 1001) to avoid "No user exists for uid" errors
# These users are only for SSH key generation - actual container runs via docker-compose user: directive
RUN groupadd -g 1000 app 2>/dev/null || true && \
    groupadd -g 1001 agent_smith 2>/dev/null || true && \
    useradd -u 1000 -g app -m -s /bin/bash app 2>/dev/null || true && \
    useradd -u 1001 -g agent_smith -m -s /bin/bash agent_smith 2>/dev/null || true && \
    mkdir -p /home/app/.nanobot /home/agent_smith/.ssh /app/config /app/ssh && \
    chmod 755 /home/app /home/agent_smith && \
    chmod 755 /home/app/.nanobot /home/agent_smith/.ssh /app/config && \
    chmod 777 /app/ssh && \
    chown -R app:app /home/app /app && \
    chown -R agent_smith:agent_smith /home/agent_smith

# Copy application files
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .
COPY templates/ templates/

# Set ownership
RUN chown -R app:app /app

EXPOSE 8899

# Default user is app - but docker-compose overrides this with user: directive
USER app

CMD ["python", "app.py"]
