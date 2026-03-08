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
    
    from .routes.auth import auth_bp                    # De auth.py
    from .routes.admin import admin_dashboard_bp        # De admin.py 
    from .routes.categorias import categorias_bp        # De categoria.py
    
    # Registrar blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_dashboard_bp)          # Registrar el blueprint admin
    app.register_blueprint(categorias_bp)               # Registrar el blueprint categoria
    
    return app

