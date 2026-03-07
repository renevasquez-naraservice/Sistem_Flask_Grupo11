from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_admin import Admin
from flask_migrate import Migrate



# Iniciaremos extensiones
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
admin = Admin(name="Panel de Administración", template_mode='bootstrap4')

# Configuración de Flask-Login
login_manager.login_view = "auth.login"
login_manager.login_message = "Por favor, inicia sesión para acceder"
login_manager.login_message_category = "info"

#Importacion modelo
from .models.user import User  
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))  