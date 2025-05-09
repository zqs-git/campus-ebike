"""Add charging pile and session tables

Revision ID: 55f0737287a7
Revises: 34816741a333
Create Date: 2025-04-22 13:51:23.803506

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '55f0737287a7'
down_revision = '34816741a333'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('charging_piles',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('location_id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=50), nullable=False),
    sa.Column('connector', sa.String(length=20), nullable=False),
    sa.Column('power_kw', sa.Float(), nullable=False),
    sa.Column('fee_rate', sa.Float(), nullable=False),
    sa.Column('status', sa.Enum('available', 'reserved', 'charging', 'finished', 'offline', name='chargingpilestatus'), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['location_id'], ['campus_locations.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('charging_sessions',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('pile_id', sa.Integer(), nullable=False),
    sa.Column('start_time', sa.DateTime(), nullable=True),
    sa.Column('end_time', sa.DateTime(), nullable=True),
    sa.Column('status', sa.Enum('reserved', 'ongoing', 'completed', 'cancelled', name='chargingsessionstatus'), nullable=False),
    sa.Column('energy_kwh', sa.Float(), nullable=True),
    sa.Column('fee_amount', sa.Float(), nullable=True),
    sa.ForeignKeyConstraint(['pile_id'], ['charging_piles.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###



def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('charging_sessions')
    op.drop_table('charging_piles')
    # ### end Alembic commands ###
