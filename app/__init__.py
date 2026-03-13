from flask import Flask
from config import Config
from .extensions import db, login_manager, admin, migrate

def create_app(config_class=Config):
    """Fábrica de aplicación"""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Inicializar extensiones
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    admin.init_app(app)
    
    # Configuración adicional
    config_class.init_app(app)
    
    # Importar modelos (para migraciones)
    from .models import user
    from .models import categoria
    from .models import producto
    from .models import pedido
    from .models import etiqueta  
    from .models import detalle_pedido
    from .models import chatbot  
    
    from .routes.auth import auth_bp                    # De auth.py
    from .routes.admin import admin_dashboard_bp        # De admin.py 
    from .routes.categorias import categorias_bp        # De categoria.py
    from .routes.productos import productos_bp
    from .routes.admin_usuarios import admin_usuarios_bp        # De admin_usuarios.py
    from .routes.pedidos import pedidos_bp        # De pedidos.py
    from .routes.detalle_pedido import detalles_pedido_bp        # De detalle_pedido.py

    from .routes.chatbot import chatbot_bp                                                      # ← NUEVO Despues borrar
    from .routes.dashboard_ia import dashboard_ia_bp                                            # ← NUEVO Despues borrar

    # Registrar blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_dashboard_bp)          # Registrar el blueprint admin
    app.register_blueprint(categorias_bp)               # Registrar el blueprint categoria
    app.register_blueprint(productos_bp)
    app.register_blueprint(admin_usuarios_bp)         # Registrar el blueprint de usuarios
    app.register_blueprint(pedidos_bp)         # Registrar el blueprint de pedidos
    app.register_blueprint(detalles_pedido_bp)         # Registrar el blueprint de detalles de pedido

    app.register_blueprint(chatbot_bp)              # Registrar el blueprint del chatbot        # ← NUEVO Despues borrar
    app.register_blueprint(dashboard_ia_bp)          # Registrar el blueprint del dashboard de  # ← NUEVO Despues borrar
    return app

