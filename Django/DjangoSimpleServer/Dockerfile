FROM python:3.11-slim

# Variables de entorno para Python
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Instalar dependencias del sistema (para MongoDB y debugging)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiar e instalar dependencias de python
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copiar codigo de la aplicacion
COPY ./car_app /app/

# Variables de entorno por defecto para MongoDB
# IMPORTANTE: Sobrescribir según tu caso:
# - MongoDB en tu PC: host.docker.internal (default)
# - MongoDB en Docker: nombre del contenedor (ej: mongodb)
# - MongoDB Atlas: usar MONGODB_URI en su lugar
ENV MONGODB_HOST=host.docker.internal
ENV MONGODB_PORT=27017
ENV MONGODB_DB=car_database
ENV MONGODB_USERNAME=
ENV MONGODB_PASSWORD=

EXPOSE 8000

CMD [ "python", "manage.py", "runserver", "0.0.0.0:8000" ]