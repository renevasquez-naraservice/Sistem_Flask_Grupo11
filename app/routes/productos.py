import os
import uuid
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from werkzeug.utils import secure_filename
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
            file = request.files['imagen_archivo']
            if file and file.filename != '':
                # Generamos nombre único para evitar conflictos y caché
                ext = os.path.splitext(file.filename)[1]
                nombre_unico = f"{uuid.uuid4().hex}{ext}"
                filename = secure_filename(nombre_unico)
                
                upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                file.save(upload_path)
                nombre_imagen = filename

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
        print(f"Error al crear producto: {e}")
        flash(f"Error al crear el producto: {str(e)}", "danger")

    return redirect(url_for("productos.lista"))

@productos_bp.route("/editar/<int:id>", methods=["POST"])
def editar(id):
    producto = Producto.query.get_or_404(id)
    
    try:
        # Actualizamos los campos de texto
        producto.nombre = request.form["nombre"]
        producto.descripcion = request.form["descripcion"]
        producto.precio = float(request.form["precio"])
        producto.stock = int(request.form["stock"])
        producto.categoria_id = int(request.form["categoria"])
        producto.activo = "activo" in request.form

        # --- MANEJO DE IMAGEN EN EDICIÓN ---
        if 'imagen_archivo' in request.files:
            file = request.files['imagen_archivo']
            if file and file.filename != '':
                # Generamos un nombre único nuevo
                ext = os.path.splitext(file.filename)[1]
                nombre_unico = f"{uuid.uuid4().hex}{ext}"
                filename = secure_filename(nombre_unico)
                
                upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                
                # Guardamos el archivo
                file.save(upload_path)
                
                # Opcional: Borrar imagen anterior si no es la default
                if producto.imagen and producto.imagen != 'default.png':
                    old_path = os.path.join(current_app.config['UPLOAD_FOLDER'], producto.imagen)
                    if os.path.exists(old_path):
                        os.remove(old_path)
                
                # Actualizamos el campo en la base de datos
                producto.imagen = filename
                print(f"DEBUG: Imagen actualizada a {filename}")

        db.session.commit()
        flash("Producto actualizado correctamente", "success")

    except Exception as e:
        db.session.rollback()
        print(f"Error crítico en editar: {e}")
        flash("Error al actualizar el producto", "danger")

    return redirect(url_for("productos.lista"))

@productos_bp.route("/eliminar/<int:id>")
def eliminar(id):
    producto = Producto.query.get_or_404(id)
    try:
        # Opcional: Borrar imagen al eliminar producto
        if producto.imagen and producto.imagen != 'default.png':
            img_path = os.path.join(current_app.config['UPLOAD_FOLDER'], producto.imagen)
            if os.path.exists(img_path):
                os.remove(img_path)
                
        db.session.delete(producto)
        db.session.commit()
        flash("Producto eliminado correctamente", "warning")
    except Exception as e:
        db.session.rollback()
        print(f"Error al eliminar: {e}")
        flash("Error al eliminar el producto", "danger")
        
    return redirect(url_for("productos.lista"))