from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from ..extensions import db
from ..models.pedido import Pedido

pedidos_bp = Blueprint(
    "pedidos",
    __name__,
    url_prefix="/pedidos"
)

@pedidos_bp.route("/")
@login_required
def lista():
    pedidos = Pedido.query.order_by.all(Pedido.fecha.desc())
    return render_template("pedidos/lista.html", pedidos=pedidos)


@pedidos_bp.route("/<int:id>")
@login_required
def ver(id):
    pedido = Pedido.query.filter_by(
        id=id,
        id_usuario=current_user.id
    ).first()

    return render_template("pedidos/ver.html", pedido=pedido)


@pedidos_bp.route("/nuevo", methods=["GET", "POST"])
@login_required
def crear():
    if request.method == "POST":
        estado = request.form.get("estado")
        total = request.form.get("total")
        notas = request.form.get("notas")

        try:
            pedido = Pedido(
                estado=estado or "pendiente",
                total=float(total) if total else 0,
                notas=notas,
                id_usuario=current_user.id
            )

            db.session.add(pedido)
            db.session.commit()
            flash("Pedido creado correctamente", "success")
            return redirect(url_for("pedidos.lista"))

        except Exception as e:
            db.session.rollback()
            flash(f"Error al crear pedido: {e}", "danger")

    return render_template("pedidos/form.html", pedido=None)


@pedidos_bp.route("/<int:id>/editar", methods=["GET", "POST"])
@login_required
def editar(id):
    pedido = Pedido.query.filter_by(
        id=id,
        id_usuario=current_user.id
    ).first_or_404()

    if request.method == "POST":
        try:
            pedido.estado = request.form.get("estado") or pedido.estado
            pedido.total = float(request.form.get("total")) if request.form.get("total") else 0
            pedido.notas = request.form.get("notas")

            db.session.commit()
            flash("Pedido actualizado correctamente", "success")
            return redirect(url_for("pedidos.ver", id=pedido.id))

        except Exception as e:
            db.session.rollback()
            flash(f"Error al actualizar pedido: {e}", "danger")

    return render_template("pedidos/form.html", pedido=pedido)


@pedidos_bp.route("/<int:id>/eliminar", methods=["POST"])
@login_required
def eliminar(id):
    pedido = Pedido.query.filter_by(
        id=id,
        id_usuario=current_user.id
    ).first_or_404()

    try:
        db.session.delete(pedido)
        db.session.commit()
        flash("Pedido eliminado correctamente", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error al eliminar pedido: {e}", "danger")

    return redirect(url_for("pedidos.lista"))