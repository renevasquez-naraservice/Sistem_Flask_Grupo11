from flask import Blueprint, render_template, request, redirect, url_for
from ..models.producto import Producto
from ..models.categoria import Categoria
from ..extensions import db

productos_bp = Blueprint(
    "productos",
    __name__,
    url_prefix="/productos"
)


@productos_bp.route("/")
def lista():

    productos = Producto.query.all()
    categorias = Categoria.query.all()

    return render_template(
        "productos/lista.html",
        productos=productos,
        categorias=categorias
    )


@productos_bp.route("/crear", methods=["POST"])
def crear():

    nombre = request.form["nombre"]
    descripcion = request.form["descripcion"]
    precio = request.form["precio"]
    stock = request.form["stock"]
    categoria = request.form["categoria"]

    activo = "activo" in request.form

    nuevo_producto = Producto(
        nombre=nombre,
        descripcion=descripcion,
        precio=precio,
        stock=stock,
        id_categoria=categoria,
        activo=activo
    )

    db.session.add(nuevo_producto)
    db.session.commit()

    return redirect(url_for("productos.lista"))


@productos_bp.route("/editar/<int:id>", methods=["POST"])
def editar(id):

    producto = Producto.query.get_or_404(id)

    producto.nombre = request.form["nombre"]
    producto.descripcion = request.form["descripcion"]
    producto.precio = request.form["precio"]
    producto.stock = request.form["stock"]
    producto.id_categoria = request.form["categoria"]

    producto.activo = "activo" in request.form

    db.session.commit()

    return redirect(url_for("productos.lista"))


@productos_bp.route("/eliminar/<int:id>")
def eliminar(id):

    producto = Producto.query.get_or_404(id)

    db.session.delete(producto)
    db.session.commit()

    return redirect(url_for("productos.lista"))