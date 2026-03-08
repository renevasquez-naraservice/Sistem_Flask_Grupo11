from flask import Blueprint, render_template
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


@categorias_bp.route("/crear")
def crear():
    return render_template("categorias/crear.html")


@categorias_bp.route("/editar/<int:id>")
def editar(id):
    categoria = Categoria.query.get_or_404(id)
    return render_template("categorias/editar.html", categoria=categoria)