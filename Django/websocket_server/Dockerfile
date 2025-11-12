# WebSocket Server - Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Copiar requirements y instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el script del servidor WebSocket
COPY websocket_server.py .

# Exponer el puerto de WebSocket
EXPOSE 8765

# Comando para iniciar el servidor WebSocket
CMD ["python", "websocket_server.py"]