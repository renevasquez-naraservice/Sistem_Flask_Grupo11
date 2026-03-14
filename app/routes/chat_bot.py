from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
import logging
import time
from ..ia.config import chatbot  # Motor de IA 

# Configuramos el Blueprint del chat
chatbot_bp = Blueprint('chat_bot', __name__)

# Logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@chatbot_bp.route('/ia/chat')
@login_required
def chat_page():
    # Asegúrate de que la ruta al archivo sea la correcta en tu proyecto
    return render_template('ia/chat_test.html')

@chatbot_bp.route('/ia/chat/historial', methods=['GET'])
@login_required
def obtener_historial():
    """ 
    Devolvemos sugerencias y un historial vacío por ahora.
    """
    try:
        sugerencias = [
            "¿Qué productos tienen poco stock?",
            "Resumen de ventas de hoy",
            "¿Cuáles son las categorías más vendidas?",
            "Estado de los últimos pedidos"
        ]
        
        return jsonify({
            'status': 'success',
            'historial': [], 
            'sugerencias': sugerencias,
            'id_conversacion': 1 # Añadimos un ID por defecto para el JS
        })
    except Exception as e:
        logger.error(f"Error en ruta historial: {e}")
        return jsonify({'status': 'error', 'historial': [], 'sugerencias': []})

@chatbot_bp.route('/ia/chat/preguntar', methods=['POST'])
@login_required
def preguntar():
    """ Maneja las preguntas y conecta con el motor de IA """
    inicio_query = time.time()
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({'status': 'error', 'respuesta': 'No llegó información.'}), 400
            
        mensaje = data.get('mensaje', '').strip()
        
        if not mensaje:
            return jsonify({'status': 'error', 'respuesta': 'El mensaje está vacío.'}), 400

        # Log de auditoría (Usamos .username o .nombre según tu modelo User)
        user_id = getattr(current_user, 'username', 'Usuario')
        logger.info(f"Usuario: {user_id} | Consulta: {mensaje}")

        try:
            # Llamamos al motor
            resultado = chatbot.procesar_mensaje(mensaje)
            
            if not resultado or 'respuesta' not in resultado:
                raise ValueError("La IA no generó una respuesta válida")

            tiempo_total = round(time.time() - inicio_query, 2)

            # Ajustamos las llaves para que el JS las lea correctamente
            return jsonify({
                'status': 'success',
                'respuesta': resultado.get('respuesta'),
                'datos': resultado.get('datos_ia'), # El JS espera 'datos'
                'tiempo': tiempo_total,
                'id_conversacion': data.get('id_conversacion', 1)
            })

        except Exception as ia_err:
            logger.error(f"Error en motor IA: {ia_err}")
            return jsonify({
                'status': 'error',
                'respuesta': "Tuve un problema al procesar la información. ¿Podrías repetir la pregunta?"
            }), 500

    except Exception as e:
        logger.error(f"Error general en ruta: {e}")
        return jsonify({'status': 'error', 'respuesta': 'Error interno del servidor.'}), 500