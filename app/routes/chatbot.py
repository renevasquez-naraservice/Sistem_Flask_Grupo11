from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from ..ia.config import chatbot, clasificador
from ..models import ConversacionChatbot, MensajeChatbot
from ..extensions import db
from datetime import datetime

chatbot_bp = Blueprint('chatbot', __name__, url_prefix='/chatbot')

@chatbot_bp.route('/')
@login_required
def index():
    """Interfaz principal del chatbot"""
    # Obtener conversaciones anteriores del usuario
    conversaciones = ConversacionChatbot.query.filter_by(
        id_usuario=current_user.id
    ).order_by(ConversacionChatbot.fecha_inicio.desc()).limit(5).all()
    
    return render_template('chatbot/index.html', 
                         conversaciones=conversaciones)

@chatbot_bp.route('/preguntar', methods=['POST'])
@login_required
def preguntar():
    """Procesa una pregunta y devuelve respuesta"""
    data = request.get_json()
    pregunta = data.get('pregunta', '').strip()
    id_conversacion = data.get('id_conversacion')
    
    if not pregunta:
        return jsonify({'error': 'Pregunta vacía'}), 400
    
    # Procesar con el chatbot
    resultado = chatbot.procesar_mensaje(pregunta, id_conversacion)
    
    return jsonify({
        'respuesta': resultado['respuesta'],
        'id_conversacion': resultado['id_conversacion'],
        'intencion': resultado['intencion']
    })

@chatbot_bp.route('/conversacion/<int:id>')
@login_required
def ver_conversacion(id):
    """Ver una conversación específica"""
    conversacion = ConversacionChatbot.query.get_or_404(id)
    
    # Verificar que pertenezca al usuario
    if conversacion.id_usuario != current_user.id:
        return jsonify({'error': 'No autorizado'}), 403
    
    mensajes = conversacion.mensajes.order_by(MensajeChatbot.fecha).all()
    
    return render_template('chatbot/conversacion.html',
                         conversacion=conversacion,
                         mensajes=mensajes)

@chatbot_bp.route('/limpiar', methods=['POST'])
@login_required
def limpiar_conversacion():
    """Inicia una nueva conversación"""
    # Crear nueva conversación
    nueva_conv = ConversacionChatbot(
        id_usuario=current_user.id,
        fecha_inicio=datetime.utcnow()
    )
    db.session.add(nueva_conv)
    db.session.commit()
    
    return jsonify({'id_conversacion': nueva_conv.id})