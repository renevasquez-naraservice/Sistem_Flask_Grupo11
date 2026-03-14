from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required
from ..ia.config import chatbot  # Ya no fallará porque instalaste openai

chatbot_bp = Blueprint('chat_bot', __name__)

@chatbot_bp.route('/ia/chat')
@login_required
def chat_page():
    return render_template('ia/chat_test.html')

@chatbot_bp.route('/ia/chat/preguntar', methods=['POST'])
@login_required
def preguntar():
    data = request.get_json()
    mensaje = data.get('mensaje')
    
    if not mensaje:
        return jsonify({'error': 'Mensaje vacío'}), 400

    # Llama al motor real que procesa la base de datos
    resultado = chatbot.procesar_mensaje(mensaje)
    
    return jsonify({
        'respuesta': resultado.get('respuesta'),
        'datos': resultado.get('datos_ia')
    })