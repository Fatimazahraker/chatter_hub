"""empty message

Revision ID: 2f64db0984f0
Revises: 05db0d395e99
Create Date: 2024-01-13 22:36:10.508598

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2f64db0984f0'
down_revision = '05db0d395e99'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('messages', schema=None) as batch_op:
        batch_op.add_column(sa.Column('image', sa.LargeBinary(), nullable=True))
        batch_op.drop_column('image_path')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('messages', schema=None) as batch_op:
        batch_op.add_column(sa.Column('image_path', sa.VARCHAR(length=255), autoincrement=False, nullable=True))
        batch_op.drop_column('image')

    # ### end Alembic commands ###