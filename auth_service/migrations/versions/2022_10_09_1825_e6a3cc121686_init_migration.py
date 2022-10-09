"""init migration

Revision ID: e6a3cc121686
Revises:
Create Date: 2022-10-09 18:25:52.985165

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'e6a3cc121686'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        'roles',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=256), nullable=True),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_roles'))
    )
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(), server_default=sa.text('uuid_generate_v4()'), nullable=False),
        sa.Column('login', sa.String(length=64), nullable=True),
        sa.Column('password', sa.Text(), nullable=True),
        sa.Column('email', sa.String(length=256), nullable=True),
        sa.Column('role_id', sa.Integer(), nullable=True),
        sa.Column('first_name', sa.String(length=256), nullable=True),
        sa.Column('last_name', sa.String(length=256), nullable=True),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['role_id'], ['roles.id'], name=op.f('fk_users_role_id_roles')),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_users'))
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('users')
    op.drop_table('roles')
    # ### end Alembic commands ###
