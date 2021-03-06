"""empty message

Revision ID: bffce3fc6a71
Revises: 28a4fb2187f8
Create Date: 2021-05-11 20:58:55.949696

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'bffce3fc6a71'
down_revision = '28a4fb2187f8'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_foreign_key(None, 'address', 'member', ['uid'], ['id'])
    op.alter_column('member', 'created_time',
               existing_type=mysql.DATETIME(),
               nullable=True)
    op.alter_column('member', 'updated_time',
               existing_type=mysql.DATETIME(),
               nullable=True)
    op.create_foreign_key(None, 'roles_users', 'role', ['role_id'], ['id'])
    op.create_foreign_key(None, 'roles_users', 'user', ['user_id'], ['id'])
    op.add_column('user', sa.Column('fs_uniquifier', sa.String(length=255), nullable=False))
    op.create_unique_constraint(None, 'user', ['fs_uniquifier'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'user', type_='unique')
    op.drop_column('user', 'fs_uniquifier')
    op.drop_constraint(None, 'roles_users', type_='foreignkey')
    op.drop_constraint(None, 'roles_users', type_='foreignkey')
    op.alter_column('member', 'updated_time',
               existing_type=mysql.DATETIME(),
               nullable=False)
    op.alter_column('member', 'created_time',
               existing_type=mysql.DATETIME(),
               nullable=False)
    op.drop_constraint(None, 'address', type_='foreignkey')
    # ### end Alembic commands ###
