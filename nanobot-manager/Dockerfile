FROM python:3.12-slim

WORKDIR /app

# Install SSH client for host-based execution and SSH key generation
RUN apt-get update && apt-get install -y --no-install-recommends openssh-client && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .
COPY templates/ templates/

EXPOSE 8899
CMD ["python", "app.py"]