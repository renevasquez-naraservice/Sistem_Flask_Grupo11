# # app/models/__init__.py
from .user import User
from .categoria import Categoria
from .producto import Producto
from .pedido import Pedido
from .etiqueta import Etiqueta
from .detalle_pedido import DetallePedido
__all__ = ['User', 'Categoria','Producto', 'Pedido', 'Etiqueta', 'DetallePedido']
