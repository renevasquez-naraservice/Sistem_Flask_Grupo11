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
        """Analiza ventas del último mes con datos"""
        
        # Obtener el último mes con ventas
        ultima_venta = Pedido.query.order_by(Pedido.fecha.desc()).first()
        if not ultima_venta:
            return None
        
        ultima_fecha = ultima_venta.fecha
        inicio_mes = ultima_fecha.replace(day=1)
        
        # Ventas del último mes con datos
        ventas_mes = db.session.query(
            func.sum(Pedido.total).label('total'),
            func.count(Pedido.id).label('cantidad')
        ).filter(
            func.date(Pedido.fecha) >= inicio_mes
        ).first()
        
        if ventas_mes and ventas_mes.total:
            # Mes anterior (mismo mes del año pasado o mes anterior)
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
                variacion = 0
                tendencia = "→"
            
            nombre_mes = ultima_fecha.strftime('%B')
            
            return {
                'tipo': 'ventas_mes',
                'titulo': f'💰 Ventas de {nombre_mes}',
                'total': ventas_mes.total,
                'cantidad': ventas_mes.cantidad,
                'mes_anterior': ventas_mes_anterior,
                'variacion': abs(variacion),
                'tendencia': tendencia,
                'descripcion': f'Ventas en {nombre_mes}: ${ventas_mes.total:,.2f} ({ventas_mes.cantidad} pedidos). {tendencia} {abs(variacion):.1f}% vs mes anterior.',
                'icono': 'bi-graph-up-arrow' if variacion > 0 else 'bi-graph-down-arrow' if variacion < 0 else 'bi-dash',
                'color': 'success' if variacion > 0 else 'danger' if variacion < 0 else 'secondary'
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
        """Genera predicciones basadas en datos REALES de la BD"""
        print("\n🔍 GENERANDO PREDICCIONES CON DATOS REALES...")
        predicciones = []
        
        # Obtener productos con stock y ventas
        resultados = db.session.query(
            Producto.id,
            Producto.nombre,
            Producto.stock,
            func.coalesce(func.sum(DetallePedido.cantidad), 0).label('total_vendido')
        ).outerjoin(DetallePedido).group_by(Producto.id).having(
            Producto.stock > 0  # Solo productos con stock
        ).all()
        
        print(f"📊 Total productos analizados: {len(resultados)}")
        
        for producto_id, nombre, stock, vendido in resultados:
            # Calcular días estimados
            if vendido > 5:  # Mínimo de ventas para considerar
                # 60 días de datos (Enero-Febrero)
                ventas_diarias = vendido / 60
                dias_restantes = int(stock / ventas_diarias) if ventas_diarias > 0 else 999
                
                # Determinar nivel de alerta
                if dias_restantes < 7:
                    nivel = '🔴 CRÍTICO'
                    color = 'danger'
                    icono = 'bi-exclamation-triangle-fill'
                elif dias_restantes < 15:
                    nivel = '🟡 PREVENTIVO'
                    color = 'warning'
                    icono = 'bi-exclamation-triangle-fill'
                elif dias_restantes < 30:
                    nivel = '🟢 SEGUIMIENTO'
                    color = 'info'
                    icono = 'bi-info-circle-fill'
                else:
                    continue  # Ignorar productos con mucho stock
                    
                print(f"   - {nombre}: stock={stock}, vendido={vendido}, días={dias_restantes} [{nivel}]")
                
                predicciones.append({
                    'tipo': 'prediccion',
                    'titulo': f'{nivel} {nombre}',
                    'producto': nombre,
                    'stock': stock,
                    'vendido': vendido,
                    'dias': dias_restantes,
                    'nivel': nivel,
                    'descripcion': f'"{nombre}" tiene {stock} unidades. Con {vendido} ventas, podría agotarse en {dias_restantes} días.',
                    'icono': icono,
                    'color': color
                })
            
            elif stock < 10:  # Stock bajo aunque no tenga ventas
                nivel = '🟡 STOCK BAJO'
                color = 'warning'
                icono = 'bi-exclamation-triangle-fill'
                
                print(f"   - {nombre}: stock bajo ({stock}) sin ventas registradas")
                
                predicciones.append({
                    'tipo': 'prediccion',
                    'titulo': f'{nivel} {nombre}',
                    'producto': nombre,
                    'stock': stock,
                    'vendido': 0,
                    'dias': 999,
                    'nivel': nivel,
                    'descripcion': f'"{nombre}" tiene solo {stock} unidades. Sin historial de ventas, pero stock crítico.',
                    'icono': icono,
                    'color': color
                })
        
        # Ordenar por días (más críticos primero)
        predicciones.sort(key=lambda x: x['dias'] if x['dias'] != 999 else 999)
        
        print(f"✅ Total predicciones generadas: {len(predicciones)}")
        return predicciones[:8]  # Top 8 predicciones