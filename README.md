- se uso Flask Framework principal utilizado para desarrollar la aplicación web. Permitió organizar rutas, vistas y lógica del sistema.
# Base de datos
Flask-SQLAlchemy==3.1.1
# Para MySQL (opcional - descomentar si se usa)
PyMySQL==1.1.0
cryptography==41.0.7

# Migraciones
Flask-Migrate==4.0.5

# Autenticación
Flask-Login==0.6.2

# Panel administrativo
Flask-Admin==1.6.1

# Formularios y validaciones
Flask-WTF==1.2.1
WTForms==3.1.0
email-validator==2.1.0

# Utilidades
python-dotenv==1.0.0
Werkzeug==2.3.7
setuptools<82
pytz==2024.1
-HTML Lenguaje usado para estructurar las vistas del sistema, como listado de pedidos, detalle, edición y formularios.
Bootstrap
-Framework de estilos utilizado para mejorar la presentación visual de las páginas y dar formato a botones, tablas, formularios y tarjetas.
-Python
Lenguaje de programación principal utilizado para desarrollar la lógica del sistema.
- MODELOS
Se crearon modelos como Pedido, producto, categoria,user, y Etiqueta para representar las tablas de la base de datos.
-Se implementaron rutas para listar, ver, editar, eliminar para los distintos modelos
-Consultas ORM
Se utilizaron métodos como query, filter_by(), first(), all() y first_or_404() para obtener datos desde la base de datos.
- plantilas Se crearon vistas para los distintos modelos
-Migraciones
Se aplicaron comandos como flask db migrate y flask db upgrade para actualizar la base de datos según los modelos.
LO APRENDIDO
-Se comprendio como se aplica el modelo, vista,controlador(MVC)
-Estructurar una aplicación web usando Flask mediante rutas, modelos y plantillas.
-Se comprendió cómo funciona la conexión entre Flask y una base de datos relacional utilizando Flask-SQLAlchemy.
-Se aprendio a crear modelos
-Se reforzó el uso de consultas ORM para filtrar, buscar, listar y mostrar registros con métodos como all(), first(), filter_by() y first_or_404().
-Se entendió la diferencia entre mostrar todos los registros y restringir resultados según el usuario autenticado.
-Se aprendió a aplicar control de acceso con login_required y validaciones con current_user.
-Se comprendió cómo diferenciar permisos entre un usuario administrador y un usuario normal dentro del sistema.
-Se reforzó el uso de condicionales en plantillas, por ejemplo para mostrar mensajes cuando no existen datos.
-Se aprendió a integrar Bootstrap para mejorar la presentación visual de las vistas.
-Se comprendió el proceso de creación y aplicación de migraciones con flask db migrate y flask db upgrade.
-Se aprendió a verificar la estructura y los datos de la base de datos desde MySQL Workbench.
-Se reforzó el trabajo con Git y GitHub para guardar cambios, usar ramas y subir avances al repositorio.
