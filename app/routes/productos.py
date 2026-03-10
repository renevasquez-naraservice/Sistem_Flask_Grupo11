import os
from werkzeug.utils import secure_filename
from flask import current_app, request, redirect, url_for, flash
from flask import Blueprint, render_template, request, redirect, url_for, flash
from ..models.producto import Producto
from ..models.categoria import Categoria
from ..extensions import db

productos_bp = Blueprint("productos", __name__, url_prefix="/productos")

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

@productos_bp.route("/")
def lista():
    # Traemos productos y categorías para la vista de impacto
    productos = Producto.query.order_by(Producto.id.desc()).all()
    categorias = Categoria.query.all()
    return render_template(
        "productos/lista.html",
        productos=productos,
        categorias=categorias
    )

@productos_bp.route("/crear", methods=["POST"])
def crear():
    try:
        # Datos de texto
        nombre = request.form["nombre"]
        descripcion = request.form["descripcion"]
        precio = float(request.form["precio"])
        stock = int(request.form["stock"])
        categoria_id = int(request.form["categoria"])
        activo = "activo" in request.form

        # Manejo de IMAGEN
        nombre_imagen = "default.png" # Valor por defecto
        
        if 'imagen_archivo' in request.files:
            file = request.files['imagen_archivo']
            if file and file.filename != '':
                filename = secure_filename(file.filename)
                # ESTA LÍNEA ES CLAVE:
                upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                print(f"DEBUG: Guardando imagen en: {upload_path}") 
        
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
        flash("Error al crear el producto", "danger")

    return redirect(url_for("productos.lista"))

@productos_bp.route("/editar/<int:id>", methods=["POST"])
def editar(id):
    producto = Producto.query.get_or_404(id)
    
    try:
        producto.nombre = request.form["nombre"]
        producto.descripcion = request.form["descripcion"]
        producto.precio = float(request.form["precio"])
        producto.stock = int(request.form["stock"])
        producto.categoria_id = int(request.form["categoria"]) # CORRECCIÓN AQUÍ
        producto.activo = "activo" in request.form

        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error al editar producto: {e}")

    return redirect(url_for("productos.lista"))

@productos_bp.route("/eliminar/<int:id>")
def eliminar(id):
    producto = Producto.query.get_or_404(id)
    try:
        db.session.delete(producto)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error al eliminar: {e}")
    return redirect(url_for("productos.lista"))