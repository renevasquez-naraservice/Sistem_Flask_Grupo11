from ..extensions import db
from datetime import datetime
class Producto(db.Model):
    __tablename__ = "productos"
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150), nullable=False)
    descripcion = db.Column(db.Text)
    precio = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, default=0)
    imagen = db.Column(db.String(200))
    activo = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    id_categoria = db.Column(
        db.Integer,
        db.ForeignKey("categorias.id"),
        nullable=False
    )
    def __repr__(self):
        return f"<Producto {self.nombre}>"