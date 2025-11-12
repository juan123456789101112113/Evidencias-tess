# WebSocket Consumer - Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Copiar requirements y instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el script del consumidor
COPY websocket_consumer.py .

# Comando para iniciar el consumidor WebSocket
CMD ["python", "websocket_consumer.py"]