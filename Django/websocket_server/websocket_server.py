"""
Servidor WebSocket para manejo de notificaciones de carros en tiempo real
Recibe y distribuye mensajes a todos los clientes conectados
"""

import asyncio
import websockets
import json
import logging
from datetime import datetime

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Conjunto de conexiones activas
connected_clients = set()

async def register_client(websocket):
    """Registra un nuevo cliente WebSocket"""
    connected_clients.add(websocket)
    logger.info(f"🔗 Nuevo cliente conectado. Total: {len(connected_clients)}")
    
    # Mensaje de bienvenida
    welcome_message = {
        "type": "connection",
        "message": "Conectado al servidor de notificaciones de carros",
        "timestamp": datetime.utcnow().isoformat() + 'Z',
        "client_count": len(connected_clients)
    }
    await websocket.send(json.dumps(welcome_message))

async def unregister_client(websocket):
    """Desregistra un cliente WebSocket de forma segura"""
    if websocket in connected_clients:
        connected_clients.discard(websocket)
        client_id = "unknown"
        try:
            if hasattr(websocket, 'remote_address') and websocket.remote_address:
                client_id = f"{websocket.remote_address[0]}:{websocket.remote_address[1]}"
        except:
            pass
        logger.info(f"❌ Cliente {client_id} desconectado. Total activos: {len(connected_clients)}")
    
    # Cerrar conexión si aún está abierta
    try:
        if not websocket.closed:
            await websocket.close()
    except:
        pass

async def broadcast_message(message):
    """Envía un mensaje a todos los clientes conectados"""
    if not connected_clients:
        logger.warning("📢 No hay clientes conectados para enviar mensaje")
        return
    
    # Crear copia del set para evitar race conditions
    clients_snapshot = connected_clients.copy()
    disconnected_clients = []
    successful_sends = 0
    
    for websocket in clients_snapshot:
        try:
            if websocket.closed:
                disconnected_clients.append(websocket)
                continue
                
            await websocket.send(json.dumps(message))
            successful_sends += 1
            
        except websockets.exceptions.ConnectionClosed:
            logger.debug(f"🔌 Conexión cerrada detectada durante broadcast")
            disconnected_clients.append(websocket)
        except Exception as e:
            logger.error(f"❌ Error inesperado enviando mensaje: {e}")
            disconnected_clients.append(websocket)
    
    # Limpiar clientes desconectados
    for websocket in disconnected_clients:
        connected_clients.discard(websocket)
    
    if disconnected_clients:
        logger.info(f"🧹 Limpiadas {len(disconnected_clients)} conexiones muertas")
    
    logger.info(f"📨 Mensaje enviado exitosamente a {successful_sends}/{len(clients_snapshot)} clientes")

async def handle_websocket_connection(websocket):
    """Maneja conexiones WebSocket individuales"""
    client_id = f"{websocket.remote_address[0]}:{websocket.remote_address[1]}"
    await register_client(websocket)
    
    try:
        # Escuchar mensajes del cliente
        async for message in websocket:
            try:
                data = json.loads(message)
                logger.info(f"📥 Mensaje recibido de {client_id}: {data.get('type', 'unknown')}")
                
                # Procesar diferentes tipos de mensajes
                if data.get("type") == "car_created":
                    car = data.get("car", {})
                    notification = {
                        "type": "car_notification",
                        "action": "created",
                        "car": car,
                        "message": f"🚗 Nuevo carro creado: {car.get('marca', 'Sin marca')} ({car.get('modelo')} año{car.get('año')})",
                        "timestamp": datetime.utcnow().isoformat() + 'Z'
                    }
                    await broadcast_message(notification)
                
                elif data.get("type") == "car_updated":
                    car = data.get("car", {})
                    notification = {
                        "type": "car_notification",
                        "action": "updated",
                        "car": car,
                        "message": f"🔄 Carro actualizado: {car.get('marca', 'Sin marca')} - {car.get('modelo')} año{car.get('año')}",
                        "timestamp": datetime.utcnow().isoformat() + 'Z'
                    }
                    await broadcast_message(notification)
                
                elif data.get("type") == "car_deleted":
                    car = data.get("car", {})
                    notification = {
                        "type": "car_notification",
                        "action": "deleted",
                        "car": car,
                        "message": f"🗑️ carro eliminado: {car.get('marca', 'Sin marca')}",
                        "timestamp": datetime.utcnow().isoformat() + 'Z'
                    }
                    await broadcast_message(notification)
                
                elif data.get("type") == "ping":
                    await websocket.send(json.dumps({
                        "type": "pong",
                        "timestamp": datetime.utcnow().isoformat() + 'Z'
                    }))
                    
                else:
                    logger.debug(f"Mensaje genérico recibido de {client_id}: {data.get('type', 'unknown')}")
                    
            except json.JSONDecodeError:
                logger.warning(f"❌ Mensaje no JSON válido de {client_id}: {message[:100]}...")
            except Exception as e:
                logger.error(f"❌ Error procesando mensaje de {client_id}: {e}")
    
    except websockets.exceptions.ConnectionClosed:
        logger.info(f"🔌 Conexión cerrada normalmente por cliente {client_id}")
    except Exception as e:
        logger.error(f"❌ Error inesperado en conexión {client_id}: {e}")
    finally:
        logger.info(f"🧹 Limpiando conexión de {client_id}")
        await unregister_client(websocket)

async def main():
    """Función principal para iniciar el servidor WebSocket"""
    # 0.0.0.0 permite conexiones desde Docker y localhost
    host = "0.0.0.0"
    port = 8765
    
    logger.info("🚀 Iniciando servidor WebSocket para Carros...")
    logger.info(f"📍 Servidor ejecutándose en ws://0.0.0.0:{port}")
    logger.info(f"📍 Accesible desde localhost en: ws://localhost:{port}")
    logger.info(f"📍 Accesible desde Docker en: ws://host.docker.internal:{port}")
    logger.info("💡 Para probar: wscat -c ws://localhost:8765")
    logger.info("⏹️  Para detener: Ctrl+C")
    
    # Iniciar servidor WebSocket
    start_server = websockets.serve(
        handle_websocket_connection,
        host,
        port
    )
    
    try:
        await start_server
        await asyncio.Future()  # Correr indefinidamente
        
    except KeyboardInterrupt:
        logger.info("⏹️ Servidor detenido por el usuario")
    except Exception as e:
        logger.error(f"❌ Error en servidor: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Servidor WebSocket detenido")