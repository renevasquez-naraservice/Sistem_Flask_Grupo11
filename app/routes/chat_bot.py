from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from ..ia.config import chatbot 
from ..models import ConversacionChatbot, MensajeChatbot
from ..extensions import db
from datetime import datetime
import logging
import time

# Usamos el prefijo /chatbot para coincidir con tu JS
chatbot_bp = Blueprint('chatbot', __name__, url_prefix='/chatbot')
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- CONFIGURACIÓN DE RESPUESTAS RÁPIDAS (Se mantienen intactas) ---
FAQ_RESPUESTAS = {
    "horario": "Nuestro horario de atención es de lunes a viernes de 8:00 AM a 6:00 PM, y sábados de 9:00 AM a 1:00 PM. 🕒",
    "contacto": "Puedes contactarnos vía WhatsApp al +591 XXXXXXXX o al correo soporte@tu-restaurante.com 📧",
    "ubicación": "Estamos ubicados en Cochabamba, Calle Principal #123. 📍",
    "hola": "¡Hola! 👋 Soy tu asistente inteligente. ¿En qué puedo ayudarte hoy?",
}

@chatbot_bp.route('/')
@login_required
def index(): # Este es el nombre de la función
    conversaciones = ConversacionChatbot.query.filter_by(id_usuario=current_user.id).all()
    return render_template('ia/chat_test.html', conversaciones=conversaciones)

@chatbot_bp.route('/preguntar', methods=['POST'])
@login_required
def preguntar():
    inicio_query = time.time()
    
    try:
        data = request.get_json()
        pregunta = data.get('pregunta', '').strip()
        id_conversacion = data.get('id_conversacion')
        
        if not pregunta:
            return jsonify({'status': 'error', 'respuesta': 'El mensaje está vacío.'}), 400
        if not id_conversacion:
            nueva_conv = ConversacionChatbot(
                id_usuario=current_user.id, 
                fecha_inicio=datetime.utcnow()
            )
            db.session.add(nueva_conv)
            db.session.commit()
            id_conversacion = nueva_conv.id

        msg_usuario = MensajeChatbot(
            id_conversacion=id_conversacion, 
            mensaje=pregunta, 
            es_usuario=True
        )
        db.session.add(msg_usuario)

        respuesta_final = None
    
        for clave, faq in FAQ_RESPUESTAS.items():
            if clave in pregunta.lower():
                respuesta_final = faq
                break

        
        if not respuesta_final:
            try:
                
                resultado_ia = chatbot.procesar_mensaje(pregunta)
                respuesta_final = resultado_ia.get('respuesta', 'No pude procesar eso.')
            except Exception as ia_err:
                logger.error(f"Error en motor IA: {ia_err}")
                respuesta_final = "Lo siento, tuve un problema al conectar con la IA."

        
        msg_bot = MensajeChatbot(
            id_conversacion=id_conversacion, 
            mensaje=respuesta_final, 
            es_usuario=False
        )
        db.session.add(msg_bot)
        db.session.commit()

        return jsonify({
            'status': 'success',
            'respuesta': respuesta_final,
            'id_conversacion': id_conversacion,
            'tiempo': round(time.time() - inicio_query, 2)
        })

    except Exception as e:
        logger.error(f"Error general en ruta preguntar: {e}")
        return jsonify({'status': 'error', 'respuesta': 'Error interno del servidor.'}), 500