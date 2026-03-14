from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from ..ia.config import analizador
import logging

logger = logging.getLogger(__name__)
dashboard_ai_bp = Blueprint('dashboard_ai', __name__)

@dashboard_ai_bp.route('/ia/dashboard')
@login_required
def dashboard_ia():
    if not getattr(current_user, 'is_admin', False):
        return "Acceso denegado", 403

    try:
        # Obtenemos la lista de insights (la que viste en analizador.py)
        raw_insights = analizador.generar_insights()
        
        # Estructura que espera el HTML
        insights_para_vista = {
            "resumen": "Generando análisis...",
            "metricas": {
                "ventas_proyectadas": "$0.00",
                "productos_criticos": 0,
                "eficiencia": "0%"
            },
            "alertas": [],
            "top_productos": []
        }

        # Mapeamos la lista de analizador.py a nuestro objeto
        for item in raw_insights:
            tipo = item.get('tipo')
            
            if tipo == 'resumen':
                insights_para_vista['resumen'] = item.get('descripcion')
            
            elif tipo == 'ventas_mes':
                insights_para_vista['metricas']['ventas_proyectadas'] = f"${item.get('total', 0):,.2f}"
            
            elif tipo == 'bajo_stock':
                insights_para_vista['metricas']['productos_criticos'] += 1
                insights_para_vista['alertas'].append(item.get('descripcion'))
                
            elif tipo == 'top_product':
                insights_para_vista['top_productos'].append(item)

        # Cálculo de eficiencia ficticio basado en stock
        if insights_para_vista['metricas']['productos_criticos'] == 0:
            insights_para_vista['metricas']['eficiencia'] = "100%"
        else:
            insights_para_vista['metricas']['eficiencia'] = "85%"

        return render_template('ia/admin_test.html', insights=insights_para_vista)

    except Exception as e:
        logger.error(f"Error en Dashboard IA: {e}")
        return render_template('ia/admin_test.html', insights={
            "resumen": "Error al conectar con el motor de IA.",
            "metricas": {"ventas_proyectadas": "$0", "productos_criticos": 0, "eficiencia": "0%"},
            "alertas": ["Revisa la conexión con Groq/Base de Datos."]
        })