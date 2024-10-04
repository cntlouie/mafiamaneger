"""Add is_admin column to User model

Revision ID: 01cebf8a5eb8
Revises: 
Create Date: 2024-10-04 20:24:52.830106

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '01cebf8a5eb8'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('faction', schema=None) as batch_op:
        batch_op.add_column(sa.Column('leader_username', sa.String(length=64), nullable=False))
        batch_op.drop_constraint('faction_leader_id_fkey', type_='foreignkey')
        batch_op.drop_column('leader_id')

    with op.batch_alter_table('stats', schema=None) as batch_op:
        batch_op.alter_column('kills',
               existing_type=sa.INTEGER(),
               type_=sa.BigInteger(),
               existing_nullable=True)
        batch_op.alter_column('destroyed_traps',
               existing_type=sa.INTEGER(),
               type_=sa.BigInteger(),
               existing_nullable=True)
        batch_op.alter_column('lost_associates',
               existing_type=sa.INTEGER(),
               type_=sa.BigInteger(),
               existing_nullable=True)
        batch_op.alter_column('lost_traps',
               existing_type=sa.INTEGER(),
               type_=sa.BigInteger(),
               existing_nullable=True)
        batch_op.alter_column('healed_associates',
               existing_type=sa.INTEGER(),
               type_=sa.BigInteger(),
               existing_nullable=True)
        batch_op.alter_column('wounded_enemy_associates',
               existing_type=sa.INTEGER(),
               type_=sa.BigInteger(),
               existing_nullable=True)
        batch_op.alter_column('eliminated_enemy_influence',
               existing_type=sa.INTEGER(),
               type_=sa.BigInteger(),
               existing_nullable=True)

    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('is_admin', sa.Boolean(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('is_admin')

    with op.batch_alter_table('stats', schema=None) as batch_op:
        batch_op.alter_column('eliminated_enemy_influence',
               existing_type=sa.BigInteger(),
               type_=sa.INTEGER(),
               existing_nullable=True)
        batch_op.alter_column('wounded_enemy_associates',
               existing_type=sa.BigInteger(),
               type_=sa.INTEGER(),
               existing_nullable=True)
        batch_op.alter_column('healed_associates',
               existing_type=sa.BigInteger(),
               type_=sa.INTEGER(),
               existing_nullable=True)
        batch_op.alter_column('lost_traps',
               existing_type=sa.BigInteger(),
               type_=sa.INTEGER(),
               existing_nullable=True)
        batch_op.alter_column('lost_associates',
               existing_type=sa.BigInteger(),
               type_=sa.INTEGER(),
               existing_nullable=True)
        batch_op.alter_column('destroyed_traps',
               existing_type=sa.BigInteger(),
               type_=sa.INTEGER(),
               existing_nullable=True)
        batch_op.alter_column('kills',
               existing_type=sa.BigInteger(),
               type_=sa.INTEGER(),
               existing_nullable=True)

    with op.batch_alter_table('faction', schema=None) as batch_op:
        batch_op.add_column(sa.Column('leader_id', sa.INTEGER(), autoincrement=False, nullable=False))
        batch_op.create_foreign_key('faction_leader_id_fkey', 'user', ['leader_id'], ['id'])
        batch_op.drop_column('leader_username')

    # ### end Alembic commands ###
