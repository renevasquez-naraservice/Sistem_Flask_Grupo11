from flask import Blueprint, render_template
from ..models.producto import Producto

productos_bp = Blueprint(
    "productos",
    __name__,
    url_prefix="/productos"
)
@productos_bp.route("/")
def lista():
    productos = Producto.query.all()

    return render_template(
        "productos/lista.html",
        productos=productos
    )