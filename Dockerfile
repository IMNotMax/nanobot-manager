FROM python:3.12-slim

WORKDIR /app

# Install SSH client for host-based execution
RUN apt-get update && apt-get install -y --no-install-recommends openssh-client && rm -rf /var/lib/apt/lists/*

COPY /app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY /app/app.py .
COPY /app/templates/ templates/

EXPOSE 8899
CMD ["python", "app.py"]