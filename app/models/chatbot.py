from ..extensions import db
from datetime import datetime

class ConversacionChatbot(db.Model):
    #almacena conversaciones completas para análisis y mejora continua
    __tablename__ = 'conversaciones_chatbot'
    
    id = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    fecha_inicio = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_fin = db.Column(db.DateTime)
    resumen = db.Column(db.Text)  # Resumen automático de la conversación
    satisfaccion = db.Column(db.Integer)  # 1-5, evaluación del usuario
    
    # Relación
    usuario = db.relationship('User', backref='conversaciones_chatbot')
    mensajes = db.relationship('MensajeChatbot', back_populates='conversacion', 
                              cascade='all, delete-orphan', lazy='dynamic')
    
    def __repr__(self):
        return f'<Conversación {self.id} - {self.fecha_inicio.strftime("%d/%m/%Y %H:%M")}>'
    
    @property
    def duracion(self):
        """Calcula la duración de la conversación en segundos"""
        if self.fecha_fin:
            delta = self.fecha_fin - self.fecha_inicio
            return delta.total_seconds()
        return None


class MensajeChatbot(db.Model):
    #almacena cada mensaje individual dentro de una conversación para análisis detallado
    __tablename__ = 'mensajes_chatbot'
    
    id = db.Column(db.Integer, primary_key=True)
    id_conversacion = db.Column(db.Integer, db.ForeignKey('conversaciones_chatbot.id'), nullable=False)
    es_usuario = db.Column(db.Boolean, default=True)  # True = usuario, False = bot
    mensaje = db.Column(db.Text, nullable=False)
    tipo_mensaje = db.Column(db.String(50))  # 'pregunta', 'respuesta', 'recomendacion', 'error'
    intencion_detectada = db.Column(db.String(100))  # 'buscar_producto', 'recomendar', 'contar', etc.
    entidades_extraidas = db.Column(db.JSON)  # Almacena datos como {'producto': 'lomo', 'categoria': 'carnes'}
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    tiempo_respuesta = db.Column(db.Float)  # Tiempo que tomó responder (ms)
    
    # Relación
    conversacion = db.relationship('ConversacionChatbot', back_populates='mensajes')
    
    def __repr__(self):
        emisor = "Usuario" if self.es_usuario else "Bot"
        return f'<Mensaje {self.id} - {emisor}: {self.mensaje[:30]}...>'


class PreguntaFrecuente(db.Model):
    #almacena preguntas frecuentes para respuestas rápidas y entrenamiento del modelo
    __tablename__ = 'preguntas_frecuentes'
    
    id = db.Column(db.Integer, primary_key=True)
    pregunta = db.Column(db.String(255), nullable=False, unique=True)
    respuesta = db.Column(db.Text, nullable=False)
    categoria = db.Column(db.String(50))  # 'productos', 'horarios', 'contacto', 'general'
    palabras_clave = db.Column(db.String(255))  # "carne, lomo, disponible"
    veces_usada = db.Column(db.Integer, default=0)
    activo = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<FAQ: {self.pregunta[:30]}...>'


class ConsultaInteligente(db.Model):
    #almacena consultas inteligentes para análisis y mejora continua
    __tablename__ = 'consultas_inteligentes'
    
    id = db.Column(db.Integer, primary_key=True)
    patron = db.Column(db.String(255), nullable=False)  # Palabras clave para identificar la consulta
    descripcion = db.Column(db.String(255))  # "Buscar productos por nombre"
    consulta_sql = db.Column(db.Text, nullable=False)  # Consulta SQL parametrizada
    tipo_resultado = db.Column(db.String(50))  # 'lista', 'conteo', 'suma', 'promedio'
    ejemplo_pregunta = db.Column(db.String(255))
    veces_usada = db.Column(db.Integer, default=0)
    
    def __repr__(self):
        return f'<ConsultaInteligente: {self.patron}>'


class RecomendacionProducto(db.Model):
    #almacena recomendaciones de productos generadas por el chatbot para análisis y mejora continua
    __tablename__ = 'recomendaciones_producto'
    
    id = db.Column(db.Integer, primary_key=True)
    id_producto = db.Column(db.Integer, db.ForeignKey('productos.id'), nullable=False)
    tipo_recomendacion = db.Column(db.String(50))  # 'mas_vendido', 'economico', 'popular', 'sugerido'
    puntuacion = db.Column(db.Float)  # Puntuación de relevancia (0-100)
    razon = db.Column(db.String(255))  # "Porque es el más vendido del mes"
    fecha_calculo = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relación
    producto = db.relationship('Producto', backref='recomendaciones')
    
    def __repr__(self):
        return f'<Recomendacion: {self.producto.nombre} - {self.tipo_recomendacion}>'


class LogInteraccionChatbot(db.Model):
    #almacena logs detallados de cada interacción para debugging y análisis de errores
    __tablename__ = 'log_interacciones_chatbot'
    
    id = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    id_conversacion = db.Column(db.Integer, db.ForeignKey('conversaciones_chatbot.id'), nullable=True)
    tipo_accion = db.Column(db.String(50))  # 'consulta', 'recomendacion', 'error'
    descripcion = db.Column(db.Text)
    datos_consulta = db.Column(db.JSON)  # Datos de la consulta en formato JSON
    resultado = db.Column(db.Text)  # Resultado de la acción
    exitoso = db.Column(db.Boolean, default=True)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relaciones
    usuario = db.relationship('User', foreign_keys=[id_usuario])
    conversacion = db.relationship('ConversacionChatbot', foreign_keys=[id_conversacion])
    
    def __repr__(self):
        return f'<Log {self.fecha} - {self.tipo_accion}>'