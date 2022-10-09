"""base roles and system user

Revision ID: 815fc57bf0da
Revises: e6a3cc121686
Create Date: 2022-10-09 19:02:05.001001

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
from sqlalchemy import text
from sqlalchemy.engine import Connection

revision = '815fc57bf0da'
down_revision = 'e6a3cc121686'
branch_labels = None
depends_on = None


def upgrade():
    conn: Connection = op.get_bind()
    roles = [
        {'id': 1, 'name': 'Administrator'},
        {'id': 2, 'name': 'Manager'},
        {'id': 3, 'name': 'User'},
    ]
    for v in roles:
        conn.execute(text("INSERT INTO ROLES (id,name) VALUES (:id,:name)"), id=v['id'], name=v['name'])

    conn.execute(
        text(
            "INSERT INTO users (id,login,password,first_name,last_name,role_id) "
            "VALUES ('1ad5ddae-03d4-49ce-9fe0-84a5a2db1980','system',null,'Главный','Попугай',1)"
        )
    )


def downgrade():
    op.execute("DELETE FROM roles WHERE id in (1,2,3)")
    op.execute("DELETE FROM users WHERE id in ('1ad5ddae-03d4-49ce-9fe0-84a5a2db1980')")
