from ..extensions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

import pytz

ZONA_HORARIA = pytz.timezone('America/La_Paz') 

class User(db.Model, UserMixin):
    """Modelo de Usuario"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    telefono = db.Column(db.String(20))
    role = db.Column(db.String(20), default='user')  # admin, user
    activo = db.Column(db.Boolean, default=True)
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    ultimo_acceso = db.Column(db.DateTime)
    
   
    # Relaciones
    pedidos = db.relationship('Pedido', back_populates='usuario', lazy='dynamic')
    
    def set_password(self, password):
        """Establecer contraseña hasheada"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verificar contraseña"""
        return check_password_hash(self.password_hash, password)
    
    def tiene_rol(self, *roles):
        """Verificar si tiene algún rol"""
        return self.role in roles
    
    @property
    def ultimo_acceso_local(self):
        """Retorna ultimo_acceso en zona horaria local"""
        if self.ultimo_acceso:
            # Si es naive (sin zona), asumimos UTC y convertimos
            if self.ultimo_acceso.tzinfo is None:
                utc_dt = pytz.utc.localize(self.ultimo_acceso)
                return utc_dt.astimezone(ZONA_HORARIA)
            # Si ya tiene zona, solo convertimos
            return self.ultimo_acceso.astimezone(ZONA_HORARIA)
        return None
    
    def set_ultimo_acceso(self):
        """Establece la hora actual en UTC"""
        self.ultimo_acceso = datetime.utcnow()
    
    @property
    def is_admin(self):
        """Verificar si es admin"""
        return self.role == 'admin'
    
    @property
    def nombre_completo(self):
        """Obtener nombre completo"""
        return f"{self.nombre} {self.apellido}"
    
    def __repr__(self):
        return f'<User {self.username}>'