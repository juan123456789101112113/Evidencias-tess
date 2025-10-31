from flask import Blueprint, render_template
from datetime import datetime
from app.models import get_db_status

pages_bp = Blueprint('pages', __name__)

@pages_bp.route('/welcome', methods=["GET"])
def welcome_page():
    """Página de bienvenida sencilla con estilos"""
    # Determinar estado de la base de datos
    db_status = "conectado" if get_db_status() else "desconectado"
    current_time = datetime.now().strftime("%H:%M:%S")
    
    return render_template('welcome.html', 
                        db_status=db_status, 
                        current_time=current_time)