from flask import Blueprint, render_template, request, redirect, url_for, flash
from ..models.categoria import Categoria
from ..extensions import db
from sqlalchemy.exc import IntegrityError # Importante para atrapar el error de relación

categorias_bp = Blueprint(
    "categorias",
    __name__,
    url_prefix="/categorias"
)

@categorias_bp.route("/")
def lista():
    categorias = Categoria.query.all()
    return render_template(
        "categorias/lista.html",
        categorias=categorias
    )

@categorias_bp.route("/crear", methods=["GET", "POST"])
def crear():
    if request.method == "POST":
        try:
            nombre = request.form["nombre"]
            descripcion = request.form["descripcion"]
            activo = "activo" in request.form

            nueva_categoria = Categoria(
                nombre=nombre,
                descripcion=descripcion,
                activo=activo
            )

            db.session.add(nueva_categoria)
            db.session.commit()
            flash("Categoría creada con éxito", "success")
            return redirect(url_for("categorias.lista"))
        except Exception as e:
            db.session.rollback()
            flash("Error al crear la categoría", "danger")

    return render_template("categorias/crear.html")

@categorias_bp.route("/editar/<int:id>", methods=["GET", "POST"])
def editar(id):
    categoria = Categoria.query.get_or_404(id)

    if request.method == "POST":
        try:
            categoria.nombre = request.form["nombre"]
            categoria.descripcion = request.form["descripcion"]
            categoria.activo = "activo" in request.form

            db.session.commit()
            flash("Categoría actualizada", "info")
            return redirect(url_for("categorias.lista"))
        except Exception as e:
            db.session.rollback()
            flash("Error al editar la categoría", "danger")

    return render_template("categorias/editar.html", categoria=categoria)

@categorias_bp.route("/eliminar/<int:id>")
def eliminar(id):
    categoria = Categoria.query.get_or_404(id)

    try:
        db.session.delete(categoria)
        db.session.commit()
        flash("Categoría eliminada con éxito", "success")
    
    except IntegrityError:
        # Este error ocurre cuando la categoría tiene productos asociados
        db.session.rollback()
        flash("No se puede eliminar: Esta categoría tiene productos asociados. Prueba desactivándola en su lugar.", "warning")
    
    except Exception as e:
        db.session.rollback()
        flash(f"Error inesperado: {str(e)}", "danger")

    return redirect(url_for("categorias.lista"))