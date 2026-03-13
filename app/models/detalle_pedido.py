from ..extensions import db
from decimal import Decimal

class DetallePedido(db.Model):
    """Modelo de Detalle de Pedido"""
    __tablename__ = 'detalles_pedido'
    
    id = db.Column(db.Integer, primary_key=True)
    cantidad = db.Column(db.Integer, nullable=False)
    precio_unitario = db.Column(db.Numeric(10, 2), nullable=False)
    
    # Claves foráneas
    id_pedido = db.Column(db.Integer, db.ForeignKey('pedidos.id'), nullable=False)
    id_producto = db.Column(db.Integer, db.ForeignKey('productos.id'), nullable=False)
    
    # Relaciones (usando strings para evitar problemas de importación circular)
    pedido = db.relationship('Pedido', backref='detalles', lazy='joined')
    producto = db.relationship('Producto', backref='detalles_pedido', lazy='joined')
    
    @property
    def subtotal(self):
        """Calcular subtotal de esta línea"""
        return self.cantidad * self.precio_unitario
    
    @property
    def subtotal_formateado(self):
        """Subtotal con formato de moneda"""
        return f"${self.subtotal:,.2f}"
    
    def __repr__(self):
        nombre = self.producto.nombre if self.producto else "Producto eliminado"
        return f'<Detalle {self.cantidad}x {nombre}>'