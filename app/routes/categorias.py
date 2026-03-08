from flask import Blueprint, render_template, request, redirect, url_for
from ..models.categoria import Categoria
from ..extensions import db

categorias_bp = Blueprint(
    "categorias",
    __name__,
    url_prefix="/categorias"
)

@categorias_bp.route("/")
def lista():
    categorias = Categoria.query.all()
    return render_template("categorias/lista.html", categorias=categorias)


@categorias_bp.route("/crear", methods=["GET", "POST"])
def crear():

    if request.method == "POST":
        nombre = request.form["nombre"]
        descripcion = request.form["descripcion"]

        nueva_categoria = Categoria(
            nombre=nombre,
            descripcion=descripcion
        )

        db.session.add(nueva_categoria)
        db.session.commit()

        return redirect(url_for("categorias.lista"))

    return render_template("categorias/crear.html")


@categorias_bp.route("/editar/<int:id>", methods=["GET", "POST"])
def editar(id):

    categoria = Categoria.query.get_or_404(id)

    if request.method == "POST":
        categoria.nombre = request.form["nombre"]
        categoria.descripcion = request.form["descripcion"]

        db.session.commit()

        return redirect(url_for("categorias.lista"))

    return render_template("categorias/editar.html", categoria=categoria)

@categorias_bp.route("/eliminar/<int:id>")
def eliminar(id):

    categoria = Categoria.query.get_or_404(id)

    db.session.delete(categoria)
    db.session.commit()

    return redirect(url_for("categorias.lista"))