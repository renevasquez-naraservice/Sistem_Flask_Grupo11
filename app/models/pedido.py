from ..extensions import db
from datetime import datetime

class Pedido(db.Model):
    __tablename__ = "pedidos"

    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    estado = db.Column(db.String(20), default="pendiente")
    total = db.Column(db.Float, default=0)
    notas = db.Column(db.Text)

    id_usuario = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    usuario = db.relationship("User", back_populates="pedidos")
    
    @property
    def total_formateado(self):
        return f"${self.total:,.2f}"

    def __repr__(self):
        return f"<Pedido {self.id}>"
    
    
    