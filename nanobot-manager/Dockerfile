FROM python:3.12-slim

WORKDIR /app

# Install SSH client for host-based execution and SSH key generation
RUN apt-get update && apt-get install -y --no-install-recommends openssh-client && rm -rf /var/lib/apt/lists/*

# Create nanobot user with UID/GID that will be mapped at runtime
# Support both 1000:1000 (default) and 1001:1001 (agent_smith on Neo)
RUN groupadd -g 1000 nanobot && \
    useradd -u 1000 -g nanobot -m -s /bin/bash nanobot && \
    groupadd -g 1001 agent_smith && \
    useradd -u 1001 -g agent_smith -m -s /bin/bash agent_smith && \
    mkdir -p /home/nanobot/.nanobot /home/nanobot/.ssh /app/config && \
    mkdir -p /home/agent_smith/.nanobot /home/agent_smith/.ssh && \
    chown -R nanobot:nanobot /home/nanobot && \
    chown -R agent_smith:agent_smith /home/agent_smith && \
    chown -R nanobot:nanobot /app

# Copy application files
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .
COPY templates/ templates/

# Set ownership
RUN chown -R nanobot:nanobot /app

EXPOSE 8899

# Switch to nanobot user (will be overridden by docker-compose user: directive)
USER nanobot

CMD ["python", "app.py"]
