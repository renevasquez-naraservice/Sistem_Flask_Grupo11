from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime

from ..extensions import db
from ..models.user import User

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

# ============================================
# LOGIN
# ============================================

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Inicio de sesión"""
    if current_user.is_authenticated:
        return redirect(url_for('auth.perfil'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        remember = True if request.form.get('remember') else False
        
        if not username or not password:
            flash('Completa todos los campos', 'error')
            return render_template('auth/login.html')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            if not user.activo:
                flash('Usuario desactivado', 'error')
                return render_template('auth/login.html')
            
            user.set_ultimo_acceso()
            db.session.commit()
            
            login_user(user, remember=remember)
            flash(f'¡Bienvenido {user.nombre}!', 'success')
            
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('auth.perfil'))
        else:
            flash('Usuario o contraseña incorrectos', 'error')
    
    return render_template('auth/login.html')

# ============================================
# REGISTRO
# ============================================

@auth_bp.route('/registro', methods=['GET', 'POST'])
def registro():
    """Registro de nuevos usuarios"""
    if current_user.is_authenticated:
        return redirect(url_for('productos.index'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        nombre = request.form.get('nombre', '').strip()
        apellido = request.form.get('apellido', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        errores = []
        
        if not all([username, email, nombre, apellido, password]):
            errores.append('Todos los campos son obligatorios')
        
        if password != confirm_password:
            errores.append('Las contraseñas no coinciden')
        
        if len(password) < 6:
            errores.append('La contraseña debe tener al menos 6 caracteres')
        
        if User.query.filter_by(username=username).first():
            errores.append('El nombre de usuario ya existe')
        
        if User.query.filter_by(email=email).first():
            errores.append('El email ya está registrado')
        
        if errores:
            for error in errores:
                flash(error, 'error')
            return render_template('auth/registro.html', form_data=request.form)
        
        try:
            user = User(
                username=username,
                email=email,
                nombre=nombre,
                apellido=apellido,
                role='user'
            )
            user.set_password(password)
            
            db.session.add(user)
            db.session.commit()
            
            flash('Registro exitoso. ¡Ya puedes iniciar sesión!', 'success')
            return redirect(url_for('auth.login'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error en el registro: {str(e)}', 'error')
    
    return render_template('auth/registro.html')

# ============================================
# LOGOUT Y PERFIL
# ============================================

@auth_bp.route('/logout')
@login_required
def logout():
    """Cerrar sesión"""
    logout_user()
    flash('Sesión cerrada', 'success')
    return redirect(url_for('auth.login'))


@auth_bp.route('/perfil')
@login_required
def perfil():
    return render_template('auth/perfil.html', user=current_user)

@auth_bp.route('/perfil/editar', methods=['GET', 'POST'])
@login_required
def editar_perfil():
    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        apellido = request.form.get('apellido', '').strip()
        email = request.form.get('email', '').strip()
        telefono = request.form.get('telefono', '').strip()
        
        if not all([nombre, apellido, email]):
            flash('Nombre, apellido y email son obligatorios', 'error')
            return render_template('auth/editar_perfil.html', user=current_user)
        
        # Verificar email único
        if email != current_user.email:
            if User.query.filter_by(email=email).first():
                flash('El email ya está en uso', 'error')
                return render_template('auth/editar_perfil.html', user=current_user)
        
        # Actualizar atributos
        current_user.nombre = nombre
        current_user.apellido = apellido
        current_user.email = email
        current_user.telefono = telefono 
        
        # Cambio de contraseña opcional
        new_password = request.form.get('new_password', '')
        if new_password:
            if len(new_password) >= 6:
                current_user.set_password(new_password)
            else:
                flash('La nueva contraseña debe tener al menos 6 caracteres', 'error')
                return render_template('auth/editar_perfil.html', user=current_user)
        
        try:
            db.session.commit()
            flash('¡Perfil actualizado con éxito!', 'success')
            return redirect(url_for('auth.perfil'))
        except Exception as e:
            db.session.rollback() 
            flash('Error al guardar los cambios. Inténtalo de nuevo.', 'error')
    
    return render_template('auth/editar_perfil.html', user=current_user)