# app/ia/analizador.py
# Analizador inteligente para generar insights automáticos en el dashboard
from sqlalchemy import func, desc, extract
from ..extensions import db
from ..models import Producto, Categoria, Pedido, DetallePedido
from datetime import datetime, timedelta
from .modelos_ia import ModeloIA
import json

class AnalizadorInteligente:
    # Genera análisis automáticos para el dashboard usando IA
    
    def __init__(self):
        self.modelo_ia = ModeloIA()
        self.nombre_negocio = "Flask Parrilla"
        
    def generar_insights(self):
        # Genera insights automáticos para el dashboard de administración
        insights = []
        
        # 1. Productos más vendidos (MÚLTIPLES)
        productos_insights = self._producto_mas_vendido()
        insights.extend(productos_insights)
        
        # 2. Categorías populares (MÚLTIPLES)
        categorias_insights = self._categorias_populares()
        insights.extend(categorias_insights)
        
        # 3. Alertas de stock bajo
        stock_bajo = self._alertas_stock()
        insights.extend(stock_bajo)
        
        # 4. Ventas del mes (SOLO 1)
        ventas_mes = self._ventas_mes()
        if ventas_mes:
            insights.append(ventas_mes)
        
        # 5. Predicciones (MÚLTIPLES)
        predicciones = self._generar_predicciones()
        insights.extend(predicciones)
        
        # 6. Resumen ejecutivo (SOLO 1)
        resumen = self._generar_resumen_ejecutivo(insights)
        if resumen:
            insights.insert(0, resumen)
        
        return insights
    def _categoria_popular(self):
        """Analiza la categoría más popular"""
        resultado = db.session.query(
            Categoria.nombre,
            func.count(Producto.id).label('total_productos'),
            func.sum(Producto.stock).label('stock_total')
        ).join(Producto).group_by(Categoria.id).order_by(
            desc('total_productos')
        ).first()
        
        if resultado:
            total_productos = Producto.query.count()
            porcentaje = (resultado[1] / total_productos * 100) if total_productos > 0 else 0
            
            return {
                'tipo': 'popular_category',
                'titulo': '📊 Categoría Popular',
                'categoria': resultado[0],
                'productos': resultado[1],
                'stock': resultado[2],
                'porcentaje': porcentaje,
                'descripcion': f'"{resultado[0]}" concentra el {porcentaje:.1f}% de los productos ({resultado[1]} items).',
                'icono': 'bi-pie-chart-fill',
                'color': 'info'
            }
        return None
    
    def _alertas_stock(self):
        # Analiza el stock de productos y genera alertas para los que están bajos o agotados
        alertas = []
        
        # Productos con stock muy bajo (menos de 5 unidades)
        muy_bajo = Producto.query.filter(Producto.stock < 5).order_by(Producto.stock).limit(3).all()
        for p in muy_bajo:
            alertas.append({
                'tipo': 'bajo_stock',
                'titulo': '⚠️ Alerta de Stock',
                'producto': p.nombre,
                'stock': p.stock,
                'descripcion': f'"{p.nombre}" tiene solo {p.stock} unidades. ¡Reabastece pronto!',
                'icono': 'bi-exclamation-triangle-fill',
                'color': 'danger'
            })
        
        # Productos agotados
        agotados = Producto.query.filter(Producto.stock == 0).count()
        if agotados > 0:
            alertas.append({
                'tipo': 'sin_stock',
                'titulo': '📦 Productos Agotados',
                'cantidad': agotados,
                'descripcion': f'{agotados} productos están actualmente agotados.',
                'icono': 'bi-box-seam',
                'color': 'secondary'
            })
        
        return alertas
    
    def _ventas_mes(self):
        """Analiza ventas del mes actual"""
        hoy = datetime.utcnow().date()
        inicio_mes = hoy.replace(day=1)
        
        ventas_mes = db.session.query(
            func.sum(Pedido.total).label('total'),
            func.count(Pedido.id).label('cantidad')
        ).filter(
            func.date(Pedido.fecha) >= inicio_mes
        ).first()
        
        if ventas_mes and ventas_mes.total:
            # Comparar con mes anterior
            mes_anterior = inicio_mes - timedelta(days=1)
            inicio_mes_anterior = mes_anterior.replace(day=1)
            
            ventas_mes_anterior = db.session.query(
                func.sum(Pedido.total).label('total')
            ).filter(
                func.date(Pedido.fecha) >= inicio_mes_anterior,
                func.date(Pedido.fecha) < inicio_mes
            ).scalar() or 0
            
            if ventas_mes_anterior > 0:
                variacion = ((ventas_mes.total - ventas_mes_anterior) / ventas_mes_anterior) * 100
                tendencia = "↑" if variacion > 0 else "↓"
            else:
                variacion = 100
                tendencia = "↑"
            
            return {
                'tipo': 'ventas_mes',
                'titulo': '💰 Ventas del Mes',
                'total': ventas_mes.total,
                'cantidad': ventas_mes.cantidad,
                'variacion': abs(variacion),
                'tendencia': tendencia,
                'descripcion': f'Ventas: ${ventas_mes.total:,.2f} ({ventas_mes.cantidad} pedidos). {tendencia} {abs(variacion):.1f}% vs mes anterior.',
                'icono': 'bi-graph-up-arrow' if variacion > 0 else 'bi-graph-down-arrow',
                'color': 'success' if variacion > 0 else 'danger'
            }
        return None
    

    def _generar_resumen_ejecutivo(self, insights):
        """Genera un resumen ejecutivo usando IA"""
        if not insights:
            return None
        
        # Construir contexto para la IA
        contexto = f"Resumen ejecutivo para {self.nombre_negocio}\n\n"
        contexto += "Datos del dashboard:\n"
        
        for insight in insights[:5]:  # Solo los primeros 5 para no saturar
            contexto += f"- {insight.get('descripcion', '')}\n"
        
        try:
            respuesta = self.modelo_ia.generar_respuesta(
                sistema="Eres un analista de negocios experto en restaurantes. Genera un resumen ejecutivo breve y profesional.",
                usuario=f"Genera un resumen de 3 líneas con estos datos:\n{contexto}",
                temperatura=0.5,
                max_tokens=150
            )
            
            return {
                'tipo': 'resumen',
                'titulo': '📋 Resumen Ejecutivo',
                'descripcion': respuesta,
                'icono': 'bi-chat-quote-fill',
                'color': 'primary'
            }
        except:
            # Si falla la IA, generar un resumen simple
            total_insights = len(insights)
            return {
                'tipo': 'resumen',
                'titulo': '📋 Resumen',
                'descripcion': f'Se han generado {total_insights} insights. Revisa las alertas de stock y ventas para tomar decisiones.',
                'icono': 'bi-info-circle-fill',
                'color': 'info'
            }


    def _producto_mas_vendido(self):
        # Analiza el producto más vendido del mes actual total 5
        resultados = db.session.query(
            Producto.nombre,
            func.sum(DetallePedido.cantidad).label('total_vendido'),
            func.sum(DetallePedido.cantidad * DetallePedido.precio_unitario).label('ingresos')
        ).join(DetallePedido).group_by(Producto.id).order_by(
            desc('total_vendido')
        ).limit(5).all()  # ← CAMBIADO DE first() A limit(5)
        
        if resultados:
            # Crear múltiples insights de productos
            productos_insights = []
            for i, res in enumerate(resultados):
                medalla = ['🏆', '🥈', '🥉', '📌', '📌'][i] if i < 5 else '📌'
                productos_insights.append({
                    'tipo': 'top_product',
                    'titulo': f'{medalla} Top {i+1}: {res[0]}',
                    'producto': res[0],
                    'cantidad': res[1],
                    'ingresos': res[2],
                    'descripcion': f'"{res[0]}" ocupa el puesto #{i+1} con {res[1]} unidades vendidas (${res[2]:,.2f}).',
                    'icono': 'bi-trophy-fill' if i == 0 else 'bi-star-fill',
                    'color': ['warning', 'secondary', 'danger', 'info', 'info'][i]
                })
            return productos_insights
        return []
    
    
    def _categorias_populares(self):
        # analiza las categorías más populares basándose en la cantidad de productos y stock total, y genera insights para cada una de ellas. Esto ayuda a identificar qué categorías tienen mayor presencia en el inventario y cuáles podrían ser las más atractivas para los clientes.
        resultados = db.session.query(
            Categoria.nombre,
            func.count(Producto.id).label('total_productos'),
            func.sum(Producto.stock).label('stock_total')
        ).join(Producto).filter(
            Categoria.activo == True
        ).group_by(Categoria.id).order_by(
            desc('total_productos')
        ).all()  # ← QUITAR EL first()
        
        if resultados:
            total_productos = Producto.query.count()
            categorias_insights = []
            for i, res in enumerate(resultados):
                porcentaje = (res[1] / total_productos * 100) if total_productos > 0 else 0
                categorias_insights.append({
                    'tipo': 'popular_category',
                    'titulo': f'📊 Categoría: {res[0]}',
                    'categoria': res[0],
                    'productos': res[1],
                    'stock': res[2],
                    'porcentaje': porcentaje,
                    'descripcion': f'"{res[0]}" tiene {res[1]} productos ({porcentaje:.1f}% del total).',
                    'icono': 'bi-pie-chart-fill',
                    'color': ['primary', 'success', 'info', 'warning', 'danger'][i % 5]
                })
            return categorias_insights
        return []

    def _generar_predicciones(self):
        # Genera predicciones simples basadas en tendencias actuales, como productos que podrían agotarse pronto o categorías que podrían volverse populares. Esto ayuda a los administradores a anticipar problemas o oportunidades.
        predicciones = []
        
        # Productos con stock BAJO (menos de 15) aunque no tengan muchas ventas
        productos_analizar = db.session.query(
            Producto,
            func.coalesce(func.sum(DetallePedido.cantidad), 0).label('total_vendido')
        ).outerjoin(DetallePedido).group_by(Producto.id).having(
            Producto.stock > 0,
            Producto.stock < 15  # ← UMBRAL MÁS BAJO
        ).order_by(Producto.stock).limit(5).all()
        
        for producto, vendido in productos_analizar:
            # Calcular días estimados (incluso sin ventas)
            if vendido > 0:
                ventas_diarias = vendido / 30  # promedio mensual
                dias_restantes = int(producto.stock / ventas_diarias) if ventas_diarias > 0 else 999
            else:
                # Si no tiene ventas, asumir rotación lenta
                dias_restantes = 30  # estimado
            
            if dias_restantes < 30:  # Menos de un mes
                nivel = '🔴 Crítico' if dias_restantes < 7 else '🟡 Preventivo'
                predicciones.append({
                    'tipo': 'prediccion',
                    'titulo': '🔮 Predicción de Inventario',
                    'producto': producto.nombre,
                    'stock_actual': producto.stock,
                    'dias': dias_restantes,
                    'nivel': nivel,
                    'descripcion': f'"{producto.nombre}" tiene {producto.stock} unidades. ' +
                                (f'Podría agotarse en {dias_restantes} días ({nivel}).' if dias_restantes < 30 
                                else 'Stock bajo, sin historial de ventas.'),
                    'icono': 'bi-graph-up-arrow',
                    'color': 'danger' if dias_restantes < 7 else 'warning'
                })
        
        return predicciones[:5]  # Top 5 predicciones