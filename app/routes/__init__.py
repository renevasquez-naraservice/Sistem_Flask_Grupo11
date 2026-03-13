# app/routes/__init__.py
from .auth import auth_bp
from .admin import admin_dashboard_bp
from .admin_usuarios import admin_usuarios_bp
from .categorias import categorias_bp
from .productos import productos_bp
from .admin_usuarios import admin_usuarios_bp
from .pedidos import pedidos_bp
from .detalle_pedido import detalles_pedido_bp
__all__ = ['auth_bp', 'admin_dashboard_bp', 'categorias_bp','productos_bp', 'admin_usuarios_bp', 'pedidos_bp', 'detalles_pedido_bp']
