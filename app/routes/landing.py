from flask import Blueprint, render_template
from ..models import Producto, Categoria, Pedido
from sqlalchemy import func, desc

landing_bp = Blueprint('landing', __name__)

@landing_bp.route('/')
def index():
    #Página principal del restaurante
    productos_destacados = Producto.query.filter_by(activo=True).limit(6).all()
    
    # Obtener categorías
    categorias = Categoria.query.filter_by(activo=True).all()
    
    # Estadísticas rápidas
    total_platos = Producto.query.filter_by(activo=True).count()
    total_clientes = 500  # Valor de ejemplo
    
    # Platos más populares (basado en ventas)
    platos_populares = Producto.query.order_by(
        Producto.veces_vendido.desc()
    ).limit(3).all() if hasattr(Producto, 'veces_vendido') else productos_destacados[:3]
    
    return render_template('landing/ver.html',
                         productos=productos_destacados,
                         categorias=categorias,
                         total_platos=total_platos,
                         total_clientes=total_clientes,
                         platos_populares=platos_populares)