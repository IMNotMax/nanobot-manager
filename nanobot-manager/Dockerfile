FROM python:3.12-slim

WORKDIR /app

# Install SSH client for host-based execution and SSH key generation
RUN apt-get update && apt-get install -y --no-install-recommends openssh-client && rm -rf /var/lib/apt/lists/*

# Create nanobot user with UID/GID that will be mapped at runtime
# Using 1000:1000 as default, will be overridden by docker-compose user: directive
RUN groupadd -g 1000 nanobot && \
    useradd -u 1000 -g nanobot -m -s /bin/bash nanobot && \
    mkdir -p /home/nanobot/.nanobot /home/nanobot/.ssh /app/config && \
    chown -R nanobot:nanobot /home/nanobot /app

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
