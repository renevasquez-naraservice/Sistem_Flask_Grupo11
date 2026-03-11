from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from ..extensions import db
from ..models.user import User
from ..utils.decorators import admin_required


admin_dashboard_bp = Blueprint('admin_dashboard', __name__, url_prefix='/admin')

# ============================================
# DASHBOARD PRINCIPAL
# ============================================

@admin_dashboard_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    """Dashboard principal con estadísticas"""
    stats = {
        'total_usuarios': User.query.count(),
        'total_activos': User.query.filter_by(activo=True).count(),
        'total_admins': User.query.filter_by(role='admin').count(),
        'total_usuarios_normales': User.query.filter_by(role='user').count()
    }
    return render_template('admin/dashboard.html', stats=stats)
