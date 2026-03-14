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
    return render_template('ia/chat_test.html')

@chatbot_bp.route('/ia/chat/historial', methods=['GET'])
@login_required
def obtener_historial():
    """ 
    Devolvemos sugerencias y un historial vacío por ahora 
    para no chocar con la base de datos si los nombres de columnas fallan.
    """
    try:
        # Estas preguntas aparecerán como botones en tu interfaz
        sugerencias = [
            "¿Qué productos tienen poco stock?",
            "Resumen de ventas de hoy",
            "¿Cuáles son las categorías más vendidas?",
            "Estado de los últimos pedidos"
        ]
        
        return jsonify({
            'status': 'success',
            'historial': [], # Temporalmente vacío para evitar errores 500
            'sugerencias': sugerencias
        })
    except Exception as e:
        logger.error(f"Error en ruta historial: {e}")
        return jsonify({'status': 'error', 'historial': []})

@chatbot_bp.route('/ia/chat/preguntar', methods=['POST'])
@login_required
def preguntar():
    """ Maneja las preguntas y conecta con el motor de IA """
    inicio_query = time.time()
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({'respuesta': 'No llegó información.'}), 400
            
        mensaje = data.get('mensaje', '').strip()
        
        if not mensaje:
            return jsonify({'respuesta': 'El mensaje está vacío.'}), 400

        # Log de auditoría
        logger.info(f"Usuario: {current_user.username} | Consulta: {mensaje}")

        try:
            # Llamamos al motor (chatbot.procesar_mensaje ya gestiona la lógica interna)
            resultado = chatbot.procesar_mensaje(mensaje)
            
            if not resultado or 'respuesta' not in resultado:
                raise ValueError("La IA no generó una respuesta válida")

            tiempo_total = round(time.time() - inicio_query, 2)

            # Devolvemos la respuesta limpia
            return jsonify({
                'respuesta': resultado.get('respuesta'),
                'datos': resultado.get('datos_ia'),
                'status': 'success',
                'tiempo': tiempo_total,
                'tiene_datos': bool(resultado.get('datos_ia'))
            })

        except Exception as ia_err:
            logger.error(f"Error en motor IA: {ia_err}")
            return jsonify({
                'respuesta': "Tuve un problema al procesar la información. ¿Podrías repetir la pregunta?",
                'status': 'error'
            }), 500

    except Exception as e:
        logger.error(f"Error general en ruta: {e}")
        return jsonify({'respuesta': 'Error interno del servidor.'}), 500