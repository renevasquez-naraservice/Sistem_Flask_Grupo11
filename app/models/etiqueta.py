from ..extensions import db

# Tabla asociativa para MANY-TO-MANY
producto_etiqueta = db.Table('producto_etiqueta',
    db.Column('producto_id', db.Integer, db.ForeignKey('productos.id'), primary_key=True),
    db.Column('etiqueta_id', db.Integer, db.ForeignKey('etiquetas.id'), primary_key=True),
    db.Column('fecha_asignacion', db.DateTime, default=db.func.current_timestamp())
)

class Etiqueta(db.Model):
    """Modelo de Etiqueta"""
    __tablename__ = 'etiquetas'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), unique=True, nullable=False)
    color = db.Column(db.String(20), default='primary') 
    
    # productos = db.relationship('Producto', secondary=producto_etiqueta,
    #                            back_populates='etiquetas', lazy='dynamic')
    
    def __repr__(self):
        return f'<Etiqueta {self.nombre}>'