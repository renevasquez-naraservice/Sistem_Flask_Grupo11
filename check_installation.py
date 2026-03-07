#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
check_installation.py - Script para verificar que todo está instalado correctamente
Ejecutar: python check_installation.py
"""

import sys
import pkg_resources

def check_python_version():
    """Verifica versión de Python"""
    print(f"📌 Python version: {sys.version}")
    required_version = (3, 8)
    current_version = (sys.version_info.major, sys.version_info.minor)
    
    if current_version >= required_version:
        print("✅ Versión de Python OK")
    else:
        print(f"❌ Se requiere Python {required_version[0]}.{required_version[1]}+")
        return False
    return True

def check_dependencies():
    """Verifica dependencias instaladas"""
    required = {
        'Flask': '2.3.3',
        'Flask-SQLAlchemy': '3.1.1',
        'Flask-Login': '0.6.2',
        'Flask-Admin': '1.6.1',
        'Flask-Migrate': '4.0.5',
        'PyMySQL': '1.1.0',
        'python-dotenv': '1.0.0',
        'reportlab': '4.2.0'
    }
    
    print("\n📦 Verificando dependencias...")
    all_ok = True
    
    for package, required_version in required.items():
        try:
            version = pkg_resources.get_distribution(package).version
            print(f"  {package:<20} {version:>10} → ✅")
        except pkg_resources.DistributionNotFound:
            print(f"  {package:<20} {'NO INSTALADO':>10} → ❌")
            all_ok = False
    
    return all_ok

def check_mysql():
    """Verifica conexión a MySQL"""
    print("\n🗄️  Verificando MySQL...")
    try:
        import pymysql
        from config import Config
        
        # Intentar conexión
        conn = pymysql.connect(
            host='localhost',
            user='root',
            password='',
            database='mysql'
        )
        conn.close()
        print("  Conexión a MySQL: ✅")
        
        # Verificar que la base de datos existe
        conn = pymysql.connect(
            host='localhost',
            user='root',
            password='',
            database='restaurante_db'
        )
        conn.close()
        print("  Base de datos 'restaurante_db': ✅")
        
    except Exception as e:
        print(f"  Error MySQL: ❌ {e}")
        return False
    
    return True

def check_env_file():
    """Verifica archivo .env"""
    print("\n🔧 Verificando archivo .env...")
    import os
    from pathlib import Path
    
    env_file = Path('.env')
    if env_file.exists():
        print("  Archivo .env: ✅")
        
        # Verificar contenido básico
        with open(env_file) as f:
            content = f.read()
            if 'SECRET_KEY' in content and 'DATABASE_URL' in content:
                print("  Variables requeridas: ✅")
            else:
                print("  Variables requeridas: ⚠️  (faltan SECRET_KEY o DATABASE_URL)")
    else:
        print("  Archivo .env: ❌ (debes crear .env desde .env.example)")
        return False
    
    return True

def main():
    """Función principal"""
    print("="*60)
    print("🔍 VERIFICACIÓN DE INSTALACIÓN - SISTEMA RESTAURANTE")
    print("="*60 + "\n")
    
    checks = [
        check_python_version(),
        check_dependencies(),
        check_mysql(),
        check_env_file()
    ]
    
    print("\n" + "="*60)
    if all(checks):
        print("✅ TODO CORRECTO - Puedes ejecutar: python run.py")
        print("   Usuario admin por defecto: admin / admin123")
    else:
        print("❌ HAY ERRORES - Revisa las recomendaciones arriba")
        print("\n📌 Pasos a seguir:")
        print("1. Instala las dependencias: pip install -r requirements.txt")
        print("2. Crea .env desde .env.example")
        print("3. Asegúrate que MySQL está corriendo")
        print("4. Crea la base de datos: CREATE DATABASE restaurante_db;")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()