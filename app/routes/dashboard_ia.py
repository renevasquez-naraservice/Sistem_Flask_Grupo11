from flask import Blueprint, render_template
from flask_login import login_required, current_user
from ..ia.config import analizador
from ..utils.decorators import admin_required

from ..models import Pedido
from ..extensions import db
from sqlalchemy import extract, func
from datetime import datetime

dashboard_ia_bp = Blueprint('dashboard_ia', __name__, url_prefix='/dashboard-ia')

@dashboard_ia_bp.route('/')
@login_required
@admin_required
def analisis():
    insights = analizador.generar_insights()
    
    # Consulta optimizada
    ventas_por_mes = db.session.query(
        extract('year', Pedido.fecha).label('anio'),
        extract('month', Pedido.fecha).label('mes'),
        func.sum(Pedido.total).label('total')
    ).group_by('anio', 'mes').order_by('anio', 'mes').all()
    
    meses = []
    ventas_mensuales = []
    
    for venta in ventas_por_mes:
        # Usamos el año real de la base de datos en lugar de estático 2026
        nombre_mes = datetime(int(venta.anio), int(venta.mes), 1).strftime('%b')
        meses.append(f"{nombre_mes} {int(venta.anio)}")
        ventas_mensuales.append(round(float(venta.total), 2))
    
    # Si no hay datos, enviamos listas vacías para que Chart.js no falle
    return render_template('dashboard_ia/analisis.html',
                         insights=insights,
                         usuario=current_user,
                         meses=meses or ["Sin datos"],
                         ventas_mensuales=ventas_mensuales or [0])

