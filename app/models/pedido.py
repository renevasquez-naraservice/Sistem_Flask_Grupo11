from flask import Blueprint, render_template
from flask_login import login_required, current_user
from ..models.pedido import Pedido

pedidos_bp = Blueprint(
    "pedidos",
    __name__,
    url_prefix="/pedidos"
)

@pedidos_bp.route("/")
@login_required
def lista():
    pedidos = Pedido.query.filter_by(id_usuario=current_user.id).all()

    return render_template(
        "pedidos/lista.html",
        pedidos=pedidos
    )

@pedidos_bp.route("/<int:id>")
@login_required
def ver(id):
    pedido = Pedido.query.get_or_404(id)

    if pedido.id_usuario != current_user.id:
        return "No autorizado", 403

    return render_template(
        "pedidos/ver.html",
        pedido=pedido
    )
    
    