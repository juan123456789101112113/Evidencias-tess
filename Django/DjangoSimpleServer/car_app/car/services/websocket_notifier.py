"""
Servicio para enviar notificaciones a través de WebSocket
Mantiene la lógica de notificaciones separada de las vistas
"""

import websockets
import asyncio
import json
import threading
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# URL del servidor WebSocket (configurable)
# Opciones:
#   - host.docker.internal:8765 (Mac/Windows con Docker Desktop)
#   - 192.168.65.2:8765 (Mac con Docker Desktop - IP alternativa)
#   - TU_IP_LOCAL:8765 (reemplazar con tu IP, ej: 192.168.1.100:8765)
#   - localhost:8765 (si Django corre fuera de Docker)
import os
WEBSOCKET_URL = os.getenv("WEBSOCKET_URL", "ws://host.docker.internal:8765")


def send_car_notification(notification_type, car_data):
    """
    Envía una notificación del carro al servidor WebSocket
    
    Args:
        notification_type (str): Tipo de notificación ('created', 'updated', 'deleted')
        car_data (dict): Datos del carro
    
    Esta función utiliza threading para no bloquear la aplicación Django
    """
    message_data = {
        "type": f"car_{notification_type}",
        "car": car_data,
        "timestamp": datetime.utcnow().isoformat() + 'Z'
    } 
    
    logger.warning("------ Mensaje enviado -----")
    
    # Ejecutar en thread separado para no bloquear Django
    thread = threading.Thread(target=_send_message_sync, args=(message_data,))
    thread.daemon = True
    thread.start()


def _send_message_sync(message_data):
    """
    Función sincrónica que ejecuta el código asíncrono de envío
    """
    try:
        asyncio.run(_async_send_message(message_data))
    except Exception as e:
        logger.error(f"Error enviando notificación WebSocket: {e}")


async def _async_send_message(message_data):
    """
    Envía el mensaje al servidor WebSocket de forma asíncrona
    """
    try:
        async with websockets.connect(WEBSOCKET_URL, timeout=2) as websocket:
            await websocket.send(json.dumps(message_data))
            logger.info(f"✅ Notificación WebSocket enviada: {message_data['type']}")
    except asyncio.TimeoutError:
        logger.warning(f"⏱️ Timeout conectando al servidor WebSocket en {WEBSOCKET_URL}")
    except ConnectionRefusedError:
        logger.warning(f"🔌 No se pudo conectar al servidor WebSocket en {WEBSOCKET_URL}")
    except Exception as e:
        logger.error(f"❌ Error enviando mensaje WebSocket: {e}")


# Funciones de conveniencia para cada tipo de notificación

def notify_car_created(car):
    """
    Notifica que se creó un nuevo carro
    
    Args:
        car: Instancia del modelo Car
    """
    car_data = {
        "car_id": str(car.id),
        "marca": car.marca,
        "modelo": car.modelo,
        "año": car.año
    }
    send_car_notification("created", car_data)


def notify_car_updated(car):
    """
    Notifica que se actualizó un carro
    
    Args:
        car: Instancia del modelo Car
    """
    car_data = {
        "car_id": str(car.id),
        "marca": car.marca,
        "modelo": car.modelo,
        "año": car.año
    }
    send_car_notification("updated", car_data)


def notify_car_deleted(car_id,car_marca):
    """
    Notifica que se eliminó un carro
        
    Args:
        car_id (str): ID del carro eliminado
        car_name (str): Nombre del carro eliminado
    """
    car_data = {
        "car_id": car_id,
        "marca": car_marca
    }
    send_car_notification("deleted", car_data)