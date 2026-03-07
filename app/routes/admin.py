from flask import Blueprint, render_template
from flask_login import login_required
from ..extensions import db
from ..models.user import User

admin_dashboard_bp = Blueprint('admin_dashboard', __name__, url_prefix='/admin')

def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from flask_login import current_user
        if not current_user.is_authenticated or not current_user.is_admin:
            return render_template('errors/403.html'), 403
        return f(*args, **kwargs)
    return decorated_function


# app/routes/admin.py

@admin_dashboard_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    stats = {
        'total_usuarios': User.query.count()
    }
    return render_template('admin/dashboard.html', stats=stats) 