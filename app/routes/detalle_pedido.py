from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, abort
from flask_login import login_required, current_user
from ..extensions import db
from ..models.pedido import Pedido
from ..models.detalle_pedido import DetallePedido
from ..models.producto import Producto
from ..models.user import User
from sqlalchemy import or_, and_
from datetime import datetime

detalles_pedido_bp = Blueprint("detalles_pedido",__name__,    url_prefix="/detalles_pedido")

# ============================================
# VISTA PRINCIPAL - ADAPTADA POR ROL
# ============================================
@detalles_pedido_bp.route("/")
@login_required
def lista():
    """Vista de pedidos adaptada según el rol del usuario"""
    
    # Parámetros de filtro comunes
    buscar = request.args.get('buscar', '').strip()
    estado = request.args.get('estado')
    fecha_desde = request.args.get('fecha_desde')
    fecha_hasta = request.args.get('fecha_hasta')
    
    # ============================================
    # ADMIN: Ve todos los pedidos
    # ============================================
    if current_user.role == 'admin':
        query = Pedido.query
        
        if buscar:
            if buscar.isdigit():
                query = query.filter(or_(
                    Pedido.id == int(buscar),
                    Pedido.notas.ilike(f"%{buscar}%"),
                    User.nombre.ilike(f"%{buscar}%"),
                    User.apellido.ilike(f"%{buscar}%")
                )).join(User, Pedido.id_usuario == User.id)
            else:
                query = query.filter(or_(
                    Pedido.notas.ilike(f"%{buscar}%"),
                    User.nombre.ilike(f"%{buscar}%"),
                    User.apellido.ilike(f"%{buscar}%")
                )).join(User, Pedido.id_usuario == User.id)
        
        template = "detalles_pedido/admin_lista.html"
    
    # ============================================
    # COCINA: Ve pedidos pendientes y en preparación
    # ============================================
    elif current_user.role == 'cocina':
        query = Pedido.query.filter(
            Pedido.estado.in_(['pendiente', 'preparacion'])
        )
        
        if buscar and buscar.isdigit():
            query = query.filter(Pedido.id == int(buscar))
        
        template = "detalles_pedido/cocina_lista.html"
    
    # ============================================
    # MESERO: Ve pedidos activos (pendiente, preparacion, listo)
    # ============================================
    elif current_user.role == 'mesero':
        query = Pedido.query.filter(
            Pedido.estado.in_(['pendiente', 'preparacion', 'listo'])
        )
        
        if buscar and buscar.isdigit():
            query = query.filter(Pedido.id == int(buscar))
        
        template = "detalles_pedido/mesero_lista.html"
    
    # ============================================
    # CLIENTE: Solo ve sus pedidos
    # ============================================
    else:
        query = Pedido.query.filter_by(id_usuario=current_user.id)
        
        if buscar:
            if buscar.isdigit():
                query = query.filter(or_(
                    Pedido.id == int(buscar),
                    Pedido.notas.ilike(f"%{buscar}%")
                ))
            else:
                query = query.filter(Pedido.notas.ilike(f"%{buscar}%"))
        
        template = "detalles_pedido/cliente_lista.html"
    
    # Filtros comunes
    if estado:
        query = query.filter(Pedido.estado == estado)
    
    if fecha_desde:
        fecha_desde_dt = datetime.strptime(fecha_desde, '%Y-%m-%d')
        query = query.filter(Pedido.fecha >= fecha_desde_dt)
    
    if fecha_hasta:
        fecha_hasta_dt = datetime.strptime(fecha_hasta, '%Y-%m-%d')
        query = query.filter(Pedido.fecha <= fecha_hasta_dt)
    
    # Ordenar y ejecutar
    pedidos = query.order_by(Pedido.fecha.desc()).all()
    
    # Obtener lista de estados para filtros
    estados = ['pendiente', 'preparacion', 'listo', 'entregado', 'pagado', 'cancelado']
    
    return render_template(template, 
                         pedidos=pedidos, 
                         estados=estados,
                         buscar=buscar,
                         current_date=datetime.now())

# ============================================
# VER DETALLE DE PEDIDO (con validación por rol)
# ============================================
@detalles_pedido_bp.route("/<int:id>")
@login_required
def ver(id):
    """Ver detalle completo de un pedido con validación de permisos"""
    
    # Buscar el pedido
    pedido = Pedido.query.get_or_404(id)
    
    # Verificar permisos según rol
    if current_user.role == 'admin':
        # Admin ve todo
        pass
    elif current_user.role == 'cocina':
        # Cocina solo ve pedidos pendientes o en preparación
        if pedido.estado not in ['pendiente', 'preparacion']:
            abort(403)
    elif current_user.role == 'mesero':
        # Mesero solo ve pedidos activos
        if pedido.estado not in ['pendiente', 'preparacion', 'listo']:
            abort(403)
    else:
        # Cliente solo ve sus pedidos
        if pedido.id_usuario != current_user.id:
            abort(403)
    
    return render_template("detalles_pedido/ver.html", pedido=pedido)

# ============================================
# CREAR NUEVO PEDIDO (solo admin o mesero)
# ============================================
@detalles_pedido_bp.route("/nuevo", methods=["GET", "POST"])
@login_required
def crear():
    """Crear nuevo pedido con detalles"""
    
    # Verificar permisos
    if current_user.role not in ['admin', 'mesero','user']:
        abort(403)
    
    if request.method == "POST":
        try:
            # Crear el pedido principal
            nuevo_pedido = Pedido(
                estado="pendiente",
                total=0.0,
                notas=request.form.get("notas", ""),
                id_usuario=current_user.id
            )
            db.session.add(nuevo_pedido)
            db.session.flush()  # Para obtener el ID
            
            # Procesar los detalles del pedido
            productos_ids = request.form.getlist('producto_id[]')
            cantidades = request.form.getlist('cantidad[]')
            
            total = 0
            for i, prod_id in enumerate(productos_ids):
                if prod_id and int(cantidades[i]) > 0:
                    producto = Producto.query.get(int(prod_id))
                    if producto and producto.activo:
                        detalle = DetallePedido(
                            cantidad=int(cantidades[i]),
                            precio_unitario=producto.precio,
                            id_pedido=nuevo_pedido.id,
                            id_producto=producto.id
                        )
                        db.session.add(detalle)
                        total += detalle.cantidad * detalle.precio_unitario
                        
                        # Reducir stock si es necesario
                        producto.stock -= detalle.cantidad
            
            # Actualizar total del pedido
            nuevo_pedido.total = total
            db.session.commit()
            
            flash("Pedido creado correctamente", "success")
            return redirect(url_for("detalles_pedido.ver", id=nuevo_pedido.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f"Error al crear pedido: {str(e)}", "danger")
    
    # GET: Mostrar formulario con productos disponibles
    productos = Producto.query.filter_by(activo=True).all()
    return render_template("detalles_pedido/form.html", pedido=None, productos=productos)

# ============================================
# EDITAR PEDIDO (solo admin)
# ============================================
@detalles_pedido_bp.route("/<int:id>/editar", methods=["GET", "POST"])
@login_required
def editar(id):
    """Editar pedido existente"""
    
    # Solo admin puede editar pedidos
    if current_user.role != 'admin':
        abort(403)
    
    pedido = Pedido.query.get_or_404(id)
    
    if request.method == "POST":
        try:
            pedido.estado = request.form.get("estado", pedido.estado)
            pedido.notas = request.form.get("notas", pedido.notas)
            
            db.session.commit()
            flash("Pedido actualizado correctamente", "success")
            return redirect(url_for("pedidos.ver", id=pedido.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f"Error al actualizar pedido: {e}", "danger")
    
    return render_template("detalles_pedido/form.html", pedido=pedido, productos=[])

# ============================================
# ACTUALIZAR ESTADO (acción rápida)
# ============================================
@detalles_pedido_bp.route("/<int:id>/estado", methods=["POST"])
@login_required
def cambiar_estado(id):
    """Cambiar estado del pedido (AJAX)"""
    
    pedido = Pedido.query.get_or_404(id)
    nuevo_estado = request.json.get('estado')
    
    # Definir transiciones permitidas por rol
    transiciones = {
        'admin': ['pendiente', 'preparacion', 'listo', 'entregado', 'pagado', 'cancelado'],
        'cocina': ['preparacion', 'listo'],
        'mesero': ['entregado', 'pagado']
    }
    
    if current_user.role in transiciones and nuevo_estado in transiciones[current_user.role]:
        pedido.estado = nuevo_estado
        db.session.commit()
        return jsonify({'success': True, 'estado': nuevo_estado})
    
    return jsonify({'success': False, 'error': 'No autorizado'}), 403

# ============================================
# ELIMINAR PEDIDO (solo admin)
# ============================================
@detalles_pedido_bp.route("/<int:id>/eliminar", methods=["POST"])
@login_required
def eliminar(id):
    """Eliminar pedido (solo admin)"""
    
    if current_user.role != 'admin':
        abort(403)
    
    pedido = Pedido.query.get_or_404(id)
    
    try:
        # Restaurar stock de productos
        for detalle in pedido.detalles:
            producto = Producto.query.get(detalle.id_producto)
            if producto:
                producto.stock += detalle.cantidad
        
        db.session.delete(pedido)
        db.session.commit()
        flash("Pedido eliminado correctamente", "success")
        
    except Exception as e:
        db.session.rollback()
        flash(f"Error al eliminar pedido: {e}", "danger")
    
    return redirect(url_for("detalles_pedido.lista"))