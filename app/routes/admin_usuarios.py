from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from ..extensions import db
from ..models.user import User
from ..utils.decorators import admin_required
from ..models.pedido import Pedido

from sqlalchemy import func

admin_usuarios_bp = Blueprint('admin_usuarios', __name__, url_prefix='/admin/usuarios')

# ============================================
# GESTIÓN DE USUARIOS (TODAS LAS RUTAS)
# ============================================

@admin_usuarios_bp.route('/usuarios')
@login_required
@admin_required
def usuarios():
    """Lista todos los usuarios con filtros"""
    busqueda = request.args.get('q', '')
    role_filtro = request.args.get('role', '')
    activo_filtro = request.args.get('activo', '')
    
    query = User.query
    
    if busqueda:
        query = query.filter(
            db.or_(
                User.username.contains(busqueda),
                User.email.contains(busqueda),
                User.nombre.contains(busqueda),
                User.apellido.contains(busqueda)
            )
        )
    
    if role_filtro:
        query = query.filter_by(role=role_filtro)
    
    if activo_filtro in ['True', 'False']:
        query = query.filter_by(activo=(activo_filtro == 'True'))
    
    usuarios = query.order_by(User.fecha_registro.desc()).all()
    roles = ['admin', 'user','user','mesero','cocina']
    
    return render_template('admin/usuarios/listar.html', 
                         usuarios=usuarios,
                         roles=roles,
                         busqueda=busqueda)

@admin_usuarios_bp.route('/usuarios/crear', methods=['GET', 'POST'])
@login_required
@admin_required
def crear():
    """Crear nuevo usuario"""
    if request.method == 'POST':
        if User.query.filter_by(username=request.form['username']).first():
            flash('El nombre de usuario ya existe', 'error')
            return render_template('admin/usuarios/crear.html', roles=['admin', 'user','mesero','cocina'])
        
        if User.query.filter_by(email=request.form['email']).first():
            flash('El email ya está registrado', 'error')
            return render_template('admin/usuarios/crear.html', roles=['admin', 'user','mesero','cocina'])

        activo = 'activo' in request.form
        
        usuario = User(
            username=request.form['username'],
            email=request.form['email'],
            nombre=request.form['nombre'],
            apellido=request.form['apellido'],
            telefono=request.form.get('telefono', ''),
            role=request.form['role'],
            activo=activo
        )
        usuario.set_password(request.form['password'])
        
        db.session.add(usuario)
        db.session.commit()
        
        flash(f'Usuario {usuario.nombre_completo} creado exitosamente', 'success')
        return redirect(url_for('admin_usuarios.usuarios'))
    
    return render_template('admin/usuarios/crear.html', roles=['admin', 'user','mesero','cocina'])

@admin_usuarios_bp.route('/usuarios/<int:id>')
@login_required
@admin_required
def ver(id):
    """Ver detalle de usuario con sus pedidos"""
    usuario = User.query.get_or_404(id)
    
    # Obtener pedidos del usuario ordenados por fecha descendente
    pedidos = Pedido.query.filter_by(id_usuario=id).order_by(Pedido.fecha.desc()).all()
    
    return render_template('admin/usuarios/ver.html',  usuario=usuario, pedidos=pedidos)

@admin_usuarios_bp.route('/usuarios/<int:id>/editar', methods=['GET', 'POST'])
@login_required
@admin_required
def editar(id):
    """Editar usuario"""
    usuario = User.query.get_or_404(id)
    
    if request.method == 'POST':
        # Actualizar campos
        usuario.nombre = request.form['nombre']
        usuario.apellido = request.form['apellido']
        usuario.email = request.form['email']
        usuario.telefono = request.form.get('telefono', '')
        usuario.role = request.form['role']
        
        usuario.activo = 'activo' in request.form
        
        # Cambiar contraseña si se proporciona
        nueva_password = request.form.get('nueva_password', '')
        if nueva_password:
            if len(nueva_password) >= 6:
                usuario.set_password(nueva_password)
            else:
                flash('La contraseña debe tener al menos 6 caracteres', 'error')
                return render_template('admin/usuarios/editar.html', 
                                     usuario=usuario, 
                                     roles=['admin', 'user'])
        
        db.session.commit()
        flash(f'Usuario {usuario.nombre_completo} actualizado', 'success')
        return redirect(url_for('admin_usuarios.ver', id=usuario.id))
    
    roles = ['admin', 'user']
    return render_template('admin/usuarios/editar.html', 
                         usuario=usuario, 
                         roles=roles)

@admin_usuarios_bp.route('/usuarios/<int:id>/toggle-activo')
@login_required
@admin_required
def toggle_activo(id):
    """Activar/desactivar usuario"""
    if id == current_user.id:
        flash('No puedes desactivar tu propio usuario', 'error')
        return redirect(url_for('admin_usuarios.usuarios'))
    
    usuario = User.query.get_or_404(id)
    usuario.activo = not usuario.activo
    db.session.commit()
    
    estado = 'activado' if usuario.activo else 'desactivado'
    flash(f'Usuario {usuario.nombre_completo} {estado} correctamente', 'success')
    return redirect(url_for('admin_usuarios.usuarios'))