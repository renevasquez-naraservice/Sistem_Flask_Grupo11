from ..extensions import db

class Categoria(db.Model):

    __tablename__ = "categorias"
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.String(200))
    activo = db.Column(db.Boolean, default=True)

    # aca esta la relacion con productos 
    #productos = db.relationship(
    #    "Producto",
    #    backref="categoria",
    #    lazy=True
    #)

    def __repr__(self):
        return f"<Categoria {self.nombre}>"