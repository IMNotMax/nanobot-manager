FROM python:3.12-slim

WORKDIR /app

# Install SSH client for host-based execution and SSH key generation
RUN apt-get update && apt-get install -y --no-install-recommends openssh-client && rm -rf /var/lib/apt/lists/*

# Create a generic app user (UID will be overridden at runtime via docker-compose user: directive)
# The directory is created with mode 755 so any UID can access it after volume mount
RUN groupadd -g 1000 app && \
    useradd -u 1000 -g app -m -s /bin/bash app && \
    mkdir -p /home/app/.nanobot /home/app/.ssh /app/config && \
    chmod 755 /home/app && \
    chmod 755 /home/app/.nanobot && \
    chmod 755 /home/app/.ssh && \
    chmod 755 /app/config && \
    chown -R app:app /home/app /app

# Copy application files
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .
COPY templates/ templates/

# Set ownership
RUN chown -R app:app /app

EXPOSE 8899

# Run as app user (UID/GID will be set by docker-compose user: directive)
USER app

CMD ["python", "app.py"]
