from flask import Blueprint, render_template
from flask_login import login_required, current_user
from ..ia.config import analizador
from ..utils.decorators import admin_required

dashboard_ia_bp = Blueprint('dashboard_ia', __name__, url_prefix='/dashboard-ia')

@dashboard_ia_bp.route('/')
@login_required
@admin_required
def analisis():
    """Dashboard inteligente con análisis de IA"""
    insights = analizador.generar_insights()
    
    return render_template('dashboard_ia/analisis.html', 
                         insights=insights,
                         usuario=current_user)