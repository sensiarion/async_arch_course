"""add default statuses

Revision ID: ab84b3dd435d
Revises: 35a06d5ad0ed
Create Date: 2022-10-10 00:17:35.893100

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = 'ab84b3dd435d'
down_revision = '35a06d5ad0ed'
branch_labels = None
depends_on = None


def upgrade():
    conn: sa.engine.Connection = op.get_bind()
    statuses = [
        {'id': 1, 'status': 'opened'},
        {'id': 2, 'status': 'closed'},
    ]
    for v in statuses:
        conn.execute(sa.text("INSERT INTO statuses (id,name) VALUES (:id,:name)"), id=v['id'], name=v['status'])


def downgrade():
    op.execute("DELETE FROM statuses WHERE id in (1,2)")
