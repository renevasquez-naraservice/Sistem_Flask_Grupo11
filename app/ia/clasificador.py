import re
from enum import Enum
from datetime import datetime

class Intencion(Enum):
    # Consultas de productos
    BUSCAR_PRODUCTOS = "buscar_productos"
    CONTAR_PRODUCTOS = "contar_productos"
    PRODUCTOS_STOCK = "productos_stock"
    PRODUCTO_MAS_VENDIDO = "producto_mas_vendido"
    PRODUCTO_ECONOMICO = "producto_economico"
    RECOMENDAR_PRODUCTOS = "recomendar_productos"
    
    # Consultas de categorías
    CATEGORIAS_POPULARES = "categorias_populares"
    PRODUCTOS_POR_CATEGORIA = "productos_por_categoria"
    
    # Consultas de pedidos/ventas
    VENTAS_TOTALES = "ventas_totales"
    VENTAS_PERIODO = "ventas_periodo"
    PEDIDOS_ACTIVOS = "pedidos_activos"
    
    # Consultas generales
    SALUDO = "saludo"
    AYUDA = "ayuda"
    DESCONOCIDO = "desconocido"

class ClasificadorIntenciones:
    #Podemos clasificar las intenciones del usuario usando patrones de texto sencillos :)
    def __init__(self):
        # Patrones para cada intención
        self.patrones = {
            Intencion.SALUDO: [
                r"hola", r"buenos días", r"buenas tardes", r"qué tal", r"saludos"
            ],
            Intencion.AYUDA: [
                r"ayuda", r"qué puedes hacer", r"funcionalidades", r"cómo funcionas"
            ],
            Intencion.BUSCAR_PRODUCTOS: [
                r"buscar", r"muéstrame", r"qué productos", r"lista.*productos",
                r"tienen.*productos", r"productos disponibles"
            ],
            Intencion.CONTAR_PRODUCTOS: [
                r"cuántos", r"cuantos", r"total.*productos", r"número.*productos",
                r"cantidad.*productos"
            ],
            Intencion.PRODUCTOS_STOCK: [
                r"stock", r"disponible", r"inventario", r"hay.*unidades",
                r"productos.*con stock", r"qué hay en existencia"
            ],
            Intencion.PRODUCTO_MAS_VENDIDO: [
                r"más vendido", r"popular", r"top", r"mejor vendido",
                r"producto estrella", r"qué es lo que más se vende"
            ],
            Intencion.PRODUCTO_ECONOMICO: [
                r"económico", r"barato", r"menor precio", r"más económico",
                r"producto económico"
            ],
            Intencion.RECOMENDAR_PRODUCTOS: [
                r"recomiéndame", r"recomienda", r"qué me sugieres",
                r"cuál debería comprar", r"qué me recomiendas"
            ],
            Intencion.CATEGORIAS_POPULARES: [
                r"categorías", r"más popular", r"categoría popular",
                r"qué categoría", r"por categoría"
            ],
            Intencion.PRODUCTOS_POR_CATEGORIA: [
                r"productos de.*categoría", r"en la categoría",
                r"productos.*categoría"
            ],
            Intencion.VENTAS_TOTALES: [
                r"ventas totales", r"cuánto hemos vendido", r"ingresos",
                r"facturación", r"total vendido"
            ],
            Intencion.VENTAS_PERIODO: [
                r"ventas.*hoy", r"ventas.*este mes", r"ventas.*esta semana",
                r"ventas.*últimos días"
            ],
            Intencion.PEDIDOS_ACTIVOS: [
                r"pedidos activos", r"pedidos pendientes", r"cuántos pedidos",
                r"órdenes activas"
            ]
        }
    
    def clasificar(self, texto):
        # Función que clasifica y devuelve al intencion del usuario
        texto = texto.lower().strip()
        
        # Verificar cada patrón
        for intencion, patrones in self.patrones.items():
            for patron in patrones:
                if re.search(patron, texto):
                    return intencion
        
        # Si no hay coincidencia, las considera como ayuda o desconocida
        if len(texto.split()) < 3:
            return Intencion.AYUDA
        
        return Intencion.DESCONOCIDO
    
    def extraer_entidades(self, texto):
        #Extrae entidades relevantes del texto como precios, fechas o categorías
        entidades = {}
        
        # Buscar precios
        precios = re.findall(r'\$?(\d+(?:\.\d+)?)', texto)
        if precios:
            entidades['precios'] = [float(p) for p in precios]
        
        # Buscar fechas relativas
        if re.search(r'hoy|hoy día', texto):
            entidades['fecha'] = 'hoy'
        elif re.search(r'este mes', texto):
            entidades['fecha'] = 'este_mes'
        elif re.search(r'esta semana', texto):
            entidades['fecha'] = 'esta_semana'
        
        # Buscar categorías
        from ..models.categoria import Categoria
        categorias = Categoria.query.all()
        for cat in categorias:
            if cat.nombre.lower() in texto:
                entidades['categoria'] = cat.nombre
                entidades['categoria_id'] = cat.id
                break
        
        return entidades


# Instancia global del clasificador
clasificador = ClasificadorIntenciones()