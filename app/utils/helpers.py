import os
from werkzeug.utils import secure_filename
from flask import current_app
import uuid

def allowed_file(filename):
    """Verificar si el archivo tiene extensión permitida"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

def save_file(file, subfolder=''):
    """Guardar archivo y retornar nombre único"""
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
        unique_name = f"{uuid.uuid4().hex}.{ext}"
        
        upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], subfolder)
        os.makedirs(upload_path, exist_ok=True)
        
        file.save(os.path.join(upload_path, unique_name))
        return unique_name
    
    return None

def formata_precio(valor):
    """Formatear precio con separador de miles"""
    return f"${valor:,.2f}"

def paginate(query, page=1, per_page=10):
    """Paginación simple"""
    offset = (page - 1) * per_page
    return query.limit(per_page).offset(offset).all()