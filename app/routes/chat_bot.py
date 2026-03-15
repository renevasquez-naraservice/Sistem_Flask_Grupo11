from flask import Blueprint, render_template, request, jsonify, abort
from flask_login import login_required, current_user
from ..ia.config import chatbot 
from ..models import ConversacionChatbot, MensajeChatbot
from ..extensions import db
from datetime import datetime
import logging
import time
chatbot_bp = Blueprint('chatbot', __name__, url_prefix='/chatbot')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- CONFIGURACIÓN DE RESPUESTAS RÁPIDAS ---
FAQ_RESPUESTAS = {
    "horario": "Nuestro horario de atención es de lunes a viernes de 8:00 AM a 6:00 PM, y sábados de 9:00 AM a 1:00 PM. 🕒",
    "contacto": "Puedes contactarnos vía WhatsApp al +591 XXXXXXXX o al correo soporte@tu-restaurante.com 📧",
    "ubicación": "Estamos ubicados en Cochabamba, Calle Principal #123. 📍",
    "hola": "¡Hola! 👋 Soy tu asistente inteligente. ¿En qué puedo ayudarte hoy?",
}

@chatbot_bp.route('/')
@login_required
def index():
    conversaciones = ConversacionChatbot.query.filter_by(
        id_usuario=current_user.id
    ).order_by(ConversacionChatbot.fecha_inicio.desc()).all()
    
    return render_template('chatbot/index.html', conversaciones=conversaciones)

@chatbot_bp.route('/ver/<int:id>')
@login_required
def ver_conversacion(id):
    conversacion = ConversacionChatbot.query.get_or_404(id)
    if conversacion.id_usuario != current_user.id:
        logger.warning(f"Usuario {current_user.id} intentó acceder al chat {id} sin permiso.")
        abort(403) 
    mensajes = MensajeChatbot.query.filter_by(
        id_conversacion=id
    ).order_by(MensajeChatbot.fecha.asc()).all()
    
    return render_template('chatbot/conversacion.html', 
                           conversacion=conversacion, 
                           mensajes=mensajes)

@chatbot_bp.route('/preguntar', methods=['POST'])
@login_required
def preguntar():
    inicio_query = time.time()
    
    try:
        data = request.get_json()
        pregunta = data.get('pregunta', '').strip()
        id_conversacion = data.get('id_conversacion')
        
        if not pregunta:
            return jsonify({'status': 'error', 'respuesta': 'Mensaje vacío'}), 400
        
        resultado_ia = chatbot.procesar_mensaje(pregunta, id_conversacion)
        
        
        id_conversacion_real = resultado_ia.get('id_conversacion')
        if not id_conversacion_real:
            nueva_conv = ConversacionChatbot(
                id_usuario=current_user.id,
                fecha_inicio=datetime.utcnow()
            )
            db.session.add(nueva_conv)
            db.session.flush()
            id_conversacion_real = nueva_conv.id
    
        msg_usuario = MensajeChatbot(
            id_conversacion=id_conversacion_real,
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
            respuesta_final = resultado_ia.get('respuesta', 'No pude procesar eso.')
        
        msg_bot = MensajeChatbot(
            id_conversacion=id_conversacion_real,
            mensaje=respuesta_final,
            es_usuario=False
        )
        db.session.add(msg_bot)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'respuesta': respuesta_final,
            'id_conversacion': id_conversacion_real,
            'tiempo': round(time.time() - inicio_query, 2)
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error: {e}")
        return jsonify({'status': 'error', 'respuesta': 'Error interno'}), 500