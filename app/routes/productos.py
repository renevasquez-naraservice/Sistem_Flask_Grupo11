import os
from werkzeug.utils import secure_filename
from flask import current_app, request, redirect, url_for, flash, Blueprint, render_template
from ..models.producto import Producto
from ..models.categoria import Categoria
from ..extensions import db

productos_bp = Blueprint("productos", __name__, url_prefix="/productos")

# --- FUNCIÓN DE APOYO PARA PROCESAR IMÁGENES ---
def procesar_imagen(file):
    if file and file.filename != '':
        filename = secure_filename(file.filename)
        # Añadimos un timestamp o prefijo para evitar colisiones de nombres
        import time
        filename = f"{int(time.time())}_{filename}"
        upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(upload_path)
        return filename
    return None

@productos_bp.route("/")
def lista():
    productos = Producto.query.order_by(Producto.id.desc()).all()
    categorias = Categoria.query.all()
    return render_template("productos/lista.html", productos=productos, categorias=categorias)

@productos_bp.route("/crear", methods=["POST"])
def crear():
    try:
        nombre = request.form["nombre"]
        descripcion = request.form["descripcion"]
        precio = float(request.form["precio"])
        stock = int(request.form["stock"])
        categoria_id = int(request.form["categoria"])
        activo = "activo" in request.form

        # Manejo de IMAGEN
        nombre_imagen = "default.png"
        if 'imagen_archivo' in request.files:
            imagen_subida = procesar_imagen(request.files['imagen_archivo'])
            if imagen_subida:
                nombre_imagen = imagen_subida

        nuevo_producto = Producto(
            nombre=nombre,
            descripcion=descripcion,
            precio=precio,
            stock=stock,
            categoria_id=categoria_id,
            imagen=nombre_imagen,
            activo=activo
        )
        
        db.session.add(nuevo_producto)
        db.session.commit()
        flash("Producto creado con éxito", "success")
        
    except Exception as e:
        db.session.rollback()
        flash(f"Error al crear: {e}", "danger")

    return redirect(url_for("productos.lista"))

@productos_bp.route("/editar/<int:id>", methods=["POST"])
def editar(id):
    producto = Producto.query.get_or_404(id)
    
    try:
        producto.nombre = request.form["nombre"]
        producto.descripcion = request.form["descripcion"]
        producto.precio = float(request.form["precio"])
        producto.stock = int(request.form["stock"])
        producto.categoria_id = int(request.form["categoria"])
        producto.activo = "activo" in request.form

        # --- LÓGICA DE IMAGEN AÑADIDA AQUÍ ---
        if 'imagen_archivo' in request.files:
            file = request.files['imagen_archivo']
            nombre_editado = procesar_imagen(file)
            if nombre_editado:
                # Opcional: Eliminar la imagen vieja del disco si no es default.png
                if producto.imagen and producto.imagen != 'default.png':
                    old_path = os.path.join(current_app.config['UPLOAD_FOLDER'], producto.imagen)
                    if os.path.exists(old_path):
                        os.remove(old_path)
                
                producto.imagen = nombre_editado

        db.session.commit()
        flash("Producto actualizado correctamente", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error al editar: {e}", "danger")

    return redirect(url_for("productos.lista"))

@productos_bp.route("/eliminar/<int:id>")
def eliminar(id):
    producto = Producto.query.get_or_404(id)
    try:
        # Borrar imagen del disco antes de borrar de la DB (opcional)
        if producto.imagen and producto.imagen != 'default.png':
            path = os.path.join(current_app.config['UPLOAD_FOLDER'], producto.imagen)
            if os.path.exists(path):
                os.remove(path)
                
        db.session.delete(producto)
        db.session.commit()
        flash("Producto eliminado", "warning")
    except Exception as e:
        db.session.rollback()
        flash("Error al eliminar", "danger")
    return redirect(url_for("productos.lista"))