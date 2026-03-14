from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
import logging
import time
from ..ia.config import chatbot 

chatbot_bp = Blueprint('chat_bot', __name__)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- CONFIGURACIÓN DE RESPUESTAS RÁPIDAS (No tan exigente) ---
FAQ_RESPUESTAS = {
    "horario": "Nuestro horario de atención es de lunes a viernes de 8:00 AM a 6:00 PM, y sábados de 9:00 AM a 1:00 PM. 🕒",
    "contacto": "Puedes contactarnos vía WhatsApp al +57 300 000 0000 o al correo soporte@laboratorio.com 📧",
    "ubicación": "Estamos ubicados en la Calle Principal #123, Edificio Innovación, Piso 2. 📍",
    "hola": "¡Hola! 👋 Soy tu asistente inteligente. ¿En qué puedo ayudarte con el stock o las ventas hoy?",
}

@chatbot_bp.route('/ia/chat')
@login_required
def chat_page():
    return render_template('ia/chat_test.html')

@chatbot_bp.route('/ia/chat/preguntar', methods=['POST'])
@login_required
def preguntar():
    inicio_query = time.time()
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({'status': 'error', 'respuesta': 'No llegó información.'}), 400
            
        mensaje = data.get('mensaje', '').lower().strip() # Pasamos a minúsculas para comparar
        
        if not mensaje:
            return jsonify({'status': 'error', 'respuesta': 'El mensaje está vacío.'}), 400

        # 1. VERIFICACIÓN RÁPIDA (FAQ)
        for clave, respuesta_rapida in FAQ_RESPUESTAS.items():
            if clave in mensaje:
                return jsonify({
                    'status': 'success',
                    'respuesta': respuesta_rapida,
                    'datos': None,
                    'tiempo': 0.01  # Casi instantáneo
                })

        # 2. SI NO ES PREGUNTA RÁPIDA, LLAMAMOS A LA IA
        user_nombre = getattr(current_user, 'nombre', 'Usuario')
        logger.info(f"Consulta IA - Usuario: {user_nombre} | Mensaje: {mensaje}")

        try:
            resultado = chatbot.procesar_mensaje(mensaje)
            
            if not resultado or 'respuesta' not in resultado:
                raise ValueError("La IA no generó una respuesta válida")

            return jsonify({
                'status': 'success',
                'respuesta': resultado.get('respuesta'),
                'datos': resultado.get('datos_ia'), 
                'tiempo': round(time.time() - inicio_query, 2)
            })

        except Exception as ia_err:
            logger.error(f"Error en motor IA: {ia_err}")
            return jsonify({
                'status': 'error',
                'respuesta': "Lo siento, tuve un problema al procesar tu consulta. ¿Puedes intentar de nuevo?"
            }), 500

    except Exception as e:
        logger.error(f"Error general en ruta preguntar: {e}")
        return jsonify({'status': 'error', 'respuesta': 'Error interno del servidor.'}), 500