from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Necesitas iniciar sesión', 'error')
            return redirect(url_for('auth.login'))
        
        if not current_user.is_admin:
            flash('Acceso denegado. Se requieren permisos de administrador.', 'error')
            return redirect(url_for('auth.perfil'))
        
        return f(*args, **kwargs)
    return decorated_function



def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Necesitas iniciar sesión', 'error')
                return redirect(url_for('auth.login'))
            
            if current_user.role not in roles:
                flash(f'Acceso denegado. Se requiere rol: {", ".join(roles)}', 'error')
                return redirect(url_for('auth.perfil'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator