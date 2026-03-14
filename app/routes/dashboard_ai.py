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
        return render_template('dashboard_ia/analisis.html', insights=insights_para_vista)

    try:
        raw_insights = analizador.generar_insights() or []
        
        insights_para_vista = {
            "resumen": "No hay un análisis disponible en este momento.",
            "metricas": {
                "ventas_proyectadas": "$0.00",
                "productos_criticos": 0,
                "eficiencia": "0%"
            },
            "alertas": [],
            "top_productos": [],
            "grafica": {
                "labels": [],
                "puntos": []
            }
        }
        

        for item in raw_insights:
            tipo = item.get('tipo')
            descripcion = item.get('descripcion', '')
            
            if tipo == 'resumen' and descripcion:
                insights_para_vista['resumen'] = descripcion
            
            elif tipo == 'ventas_mes':
                total = item.get('total', 0)
                insights_para_vista['metricas']['ventas_proyectadas'] = f"${total:,.2f}"
            
            elif tipo == 'bajo_stock':
                insights_para_vista['metricas']['productos_criticos'] += 1
                if descripcion:
                    insights_para_vista['alertas'].append(descripcion)
                
            elif tipo == 'top_product':
                insights_para_vista['top_productos'].append(item)
                # Lógica para la gráfica
                nombre = item.get('nombre') or item.get('producto') or 'Producto'
                cantidad = item.get('total_vendido') or item.get('cantidad') or 0
                insights_para_vista['grafica']['labels'].append(nombre)
                insights_para_vista['grafica']['puntos'].append(cantidad)

        criticos = insights_para_vista['metricas']['productos_criticos']
        if criticos == 0:
            insights_para_vista['metricas']['eficiencia'] = "100%"
        elif criticos < 5:
            insights_para_vista['metricas']['eficiencia'] = "85%"
        else:
            insights_para_vista['metricas']['eficiencia'] = "60%"

        return render_template('dashboard_ia/analisis.html', insights=insights_para_vista)

    except Exception as e:
        logger.error(f"Error crítico en Dashboard IA: {str(e)}")
        return render_template('dashboard_ia/analisis.html', insights={
            "resumen": "Error al conectar con el motor de IA.",
            "metricas": {"ventas_proyectadas": "$0.00", "productos_criticos": 0, "eficiencia": "N/A"},
            "alertas": ["Error técnico al recuperar alertas."],
            "top_productos": [],
            "grafica": {"labels": [], "puntos": []}
        })