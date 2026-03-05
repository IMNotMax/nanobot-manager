FROM python:3.12-slim

WORKDIR /app
COPY /app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY /app/app.py .
COPY /app/templates/ templates/

EXPOSE 8899
CMD ["python", "app.py"]