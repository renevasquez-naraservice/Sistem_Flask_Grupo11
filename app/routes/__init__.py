# app/routes/__init__.py
from .auth import auth_bp
from .admin import admin_dashboard_bp

__all__ = ['auth_bp', 'admin_dashboard_bp']
