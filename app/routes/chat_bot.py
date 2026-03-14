from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
import logging
from ..ia.config import chatbot  # Motor de IA de Rene

# Configuramos el Blueprint del chat
chatbot_bp = Blueprint('chat_bot', __name__)

# Logs para pillar errores rápido en consola
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@chatbot_bp.route('/ia/chat')
@login_required
def chat_page():
    # Solo renderiza la interfaz, el trabajo sucio lo hace la ruta de abajo
    return render_template('ia/chat_test.html')

@chatbot_bp.route('/ia/chat/preguntar', methods=['POST'])
@login_required
def preguntar():
    """ Maneja las preguntas, conecta con el motor y devuelve la data """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'respuesta': 'No llegó nada de info.'}), 400
            
        # Limpiamos el mensaje (quitamos espacios basura)
        mensaje = data.get('mensaje', '').strip()
        
        if not mensaje:
            return jsonify({'respuesta': 'El mensaje está vacío, escribe algo.'}), 400

        # Log para saber qué usuario está consultando
        logger.info(f"User: {current_user.username} | Msg: {mensaje}")

        try:
            # Aquí le pasamos la bola al motor de IA
            resultado = chatbot.procesar_mensaje(mensaje)
            
            if not resultado or 'respuesta' not in resultado:
                raise ValueError("La IA no soltó respuesta")

            # Devolvemos la respuesta de la IA y los datos que sacó de la BD
            return jsonify({
                'respuesta': resultado.get('respuesta'),
                'datos': resultado.get('datos_ia'),
                'status': 'success'
            })

        except Exception as ia_err:
            logger.error(f"Fallo en el cerebro IA: {ia_err}")
            return jsonify({
                'respuesta': "La IA se mareó un poco. Intenta de nuevo.",
                'status': 'error'
            }), 500

    except Exception as e:
        logger.error(f"Error general: {e}")
        return jsonify({'respuesta': 'Error interno del servidor.'}), 500