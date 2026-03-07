"""initial schema

Revision ID: 22d9a94b72f2
Revises: 
Create Date: 2026-03-07 17:42:46.471631

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '22d9a94b72f2'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Tabla users
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(length=80), nullable=False),
        sa.Column('email', sa.String(length=120), nullable=False),
        sa.Column('password_hash', sa.String(length=200), nullable=False),
        sa.Column('nombre', sa.String(length=100), nullable=False),
        sa.Column('apellido', sa.String(length=100), nullable=False),
        sa.Column('telefono', sa.String(length=20), nullable=True),
        sa.Column('role', sa.String(length=20), server_default='user'),
        sa.Column('activo', sa.Boolean(), server_default='1'),
        sa.Column('fecha_registro', sa.DateTime(), nullable=True),
        sa.Column('ultimo_acceso', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('username'),
        sa.UniqueConstraint('email')
    )

def downgrade():
    op.drop_table('users')
