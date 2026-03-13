# app/ia/consultas.py
from sqlalchemy import func, desc, extract
from ..extensions import db
from ..models import Producto, Categoria, Pedido, DetallePedido, User
from datetime import datetime, timedelta

class ConsultasInteligentes:
    #ejecuta consultas razonables basadas en intenciones del usuario
    def __init__(self):
        self.resultados = {}
    
    def ejecutar(self, intencion, entidades=None):
        # Consulta en base a la intención y entidades extraídas
        if intencion.value == "buscar_productos":
            return self._buscar_productos(entidades)
        
        elif intencion.value == "contar_productos":
            return self._contar_productos()
        
        elif intencion.value == "productos_stock":
            return self._productos_con_stock()
        
        elif intencion.value == "producto_mas_vendido":
            return self._producto_mas_vendido()
        
        elif intencion.value == "producto_economico":
            return self._producto_economico()
        
        elif intencion.value == "recomendar_productos":
            return self._recomendar_productos(entidades)
        
        elif intencion.value == "categorias_populares":
            return self._categorias_populares()
        
        elif intencion.value == "ventas_totales":
            return self._ventas_totales(entidades)
        
        elif intencion.value == "pedidos_activos":
            return self._pedidos_activos()
        
        return {"error": "No se pudo procesar la consulta"}
    
    def _buscar_productos(self, entidades=None):
        #funcino de búsqueda de productos con filtros básicos
        query = Producto.query.filter_by(activo=True)
        
        if entidades and entidades.get('categoria_id'):
            query = query.filter_by(categoria_id=entidades['categoria_id'])
        
        productos = query.limit(10).all()
        
        return {
            'tipo': 'lista_productos',
            'productos': productos,
            'total': len(productos),
            'mensaje': f"Encontré {len(productos)} productos"
        }
    
    def _contar_productos(self):
       #función para contar productos activos e inactivos
        total = Producto.query.count()
        activos = Producto.query.filter_by(activo=True).count()
        inactivos = total - activos
        
        return {
            'tipo': 'conteo',
            'total': total,
            'activos': activos,
            'inactivos': inactivos,
            'mensaje': f"Hay {total} productos en total, {activos} activos y {inactivos} inactivos."
        }
    
    def _productos_con_stock(self):
        #listar productos disponibles
        con_stock = Producto.query.filter(Producto.stock > 0).order_by(Producto.stock.desc()).all()
        sin_stock = Producto.query.filter(Producto.stock == 0).count()
        bajo_stock = Producto.query.filter(Producto.stock < 5).count()
        
        return {
            'tipo': 'stock',
            'con_stock': con_stock[:10],  # Top 10
            'total_con_stock': len(con_stock),
            'sin_stock': sin_stock,
            'bajo_stock': bajo_stock,
            'mensaje': f"Hay {len(con_stock)} productos con stock. {bajo_stock} tienen stock bajo."
        }
    
    def _producto_mas_vendido(self):
        #Sacar cual es el producto más vendido basado en detalles de pedidos
        resultado = db.session.query(
            Producto.nombre,
            func.sum(DetallePedido.cantidad).label('total_vendido'),
            func.count(DetallePedido.id).label('veces_comprado')
        ).join(DetallePedido).group_by(Producto.id).order_by(
            desc('total_vendido')
        ).first()
        
        if resultado:
            return {
                'tipo': 'top_producto',
                'nombre': resultado[0],
                'total_vendido': resultado[1],
                'veces_comprado': resultado[2],
                'mensaje': f"El producto más vendido es '{resultado[0]}' con {resultado[1]} unidades vendidas."
            }
        
        return {'mensaje': "Aún no hay ventas registradas."}
    
    def _producto_economico(self):
        """Encuentra el producto más económico"""
        producto = Producto.query.filter_by(activo=True).order_by(Producto.precio).first()
        
        if producto:
            return {
                'tipo': 'economico',
                'producto': producto,
                'mensaje': f"El producto más económico es '{producto.nombre}' a ${producto.precio:.2f}."
            }
        
        return {'mensaje': "No hay productos disponibles."}
    
    def _recomendar_productos(self, entidades=None):
        # Que te recomiende
        # Productos populares (basado en ventas)
        populares = db.session.query(
            Producto,
            func.sum(DetallePedido.cantidad).label('total_vendido')
        ).outerjoin(DetallePedido).filter(
            Producto.activo == True,
            Producto.stock > 0
        ).group_by(Producto.id).order_by(
            desc('total_vendido')
        ).limit(5).all()
        
        recomendados = [p[0] for p in populares]
        
        # Si no hay ventas, recomendar por disponibilidad
        if not recomendados:
            recomendados = Producto.query.filter(
                Producto.activo == True,
                Producto.stock > 0
            ).order_by(Producto.stock.desc()).limit(5).all()
        
        return {
            'tipo': 'recomendaciones',
            'recomendados': recomendados,
            'mensaje': f"Te recomiendo estos {len(recomendados)} productos:"
        }
    
    def _categorias_populares(self):
        # revisa las categorias mas populares
        categorias = db.session.query(
            Categoria.nombre,
            func.count(Producto.id).label('total_productos'),
            func.sum(Producto.stock).label('stock_total')
        ).join(Producto).filter(
            Categoria.activo == True
        ).group_by(Categoria.id).order_by(
            desc('total_productos')
        ).all()
        
        return {
            'tipo': 'categorias',
            'categorias': categorias,
            'mensaje': f"Tenemos {len(categorias)} categorías activas."
        }
    
    def _ventas_totales(self, entidades=None):
        # Calcula ventas totales con filtros de fecha
        query = db.session.query(func.sum(Pedido.total).label('total'))
        
        if entidades and entidades.get('fecha'):
            hoy = datetime.utcnow().date()
            if entidades['fecha'] == 'hoy':
                query = query.filter(func.date(Pedido.fecha) == hoy)
            elif entidades['fecha'] == 'este_mes':
                query = query.filter(
                    extract('month', Pedido.fecha) == hoy.month,
                    extract('year', Pedido.fecha) == hoy.year
                )
            elif entidades['fecha'] == 'esta_semana':
                inicio_semana = hoy - timedelta(days=hoy.weekday())
                query = query.filter(func.date(Pedido.fecha) >= inicio_semana)
        
        total = query.scalar() or 0
        
        return {
            'tipo': 'ventas',
            'total': total,
            'mensaje': f"Las ventas totales son ${total:.2f}"
        }
    
    def _pedidos_activos(self):
        # Cuenta pedidos activos por estado
        pendientes = Pedido.query.filter_by(estado='pendiente').count()
        preparacion = Pedido.query.filter_by(estado='preparacion').count()
        listos = Pedido.query.filter_by(estado='listo').count()
        
        return {
            'tipo': 'pedidos',
            'pendientes': pendientes,
            'preparacion': preparacion,
            'listos': listos,
            'mensaje': f"Hay {pendientes} pedidos pendientes, {preparacion} en preparación y {listos} listos."
        }

