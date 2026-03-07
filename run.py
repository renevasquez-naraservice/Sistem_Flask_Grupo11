from app import create_app
from app.extensions import db
from app.models.user import User

from flask import redirect, url_for

app = create_app()

@app.route('/')
def index():
    return redirect(url_for('auth.login'))

@app.shell_context_processor
def make_shell_context():
    """Contexto para flask shell"""
    return {
        'db': db,
        'User': User,
    }

if __name__ == '__main__':
    with app.app_context():
        try:
            # Crear tablas
            db.create_all()
            print("=> Las tablas se han verificado/creado correctamente.")
            
            # Crear usuario admin por defecto
            if not User.query.filter_by(username='admin').first():
                admin = User(
                    username='admin',
                    email='admin@plantilla.com',
                    nombre='Admin',
                    apellido='Sistema',
                    role='admin',
                    activo=True
                )
                admin.set_password('admin123')
                db.session.add(admin)
                print("=> Usuario admin creado: admin/admin123")
            db.session.commit()
            
        except Exception as e:
            print(f"Tenemos  => Error: {e}")
    
    print("\n" + "="*50)
    print("🚀 Servidor iniciado")
    print("📍 http://localhost:5000")
    print("👤 Admin: admin / admin123")
    print("="*50 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)

