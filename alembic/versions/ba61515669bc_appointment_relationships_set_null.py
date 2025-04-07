"""Appointment relationships set null

Revision ID: ba61515669bc
Revises: 0a0060351f1c
Create Date: 2025-04-06 20:54:47.844869

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = 'ba61515669bc'
down_revision: Union[str, None] = '0a0060351f1c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('appointments', 'client_id',
               existing_type=mysql.INTEGER(),
               nullable=True)
    op.alter_column('appointments', 'service_id',
               existing_type=mysql.INTEGER(),
               nullable=True)
    op.alter_column('appointments', 'professional_id',
               existing_type=mysql.INTEGER(),
               nullable=True)
    op.drop_constraint('appointments_ibfk_1', 'appointments', type_='foreignkey')
    op.drop_constraint('appointments_ibfk_2', 'appointments', type_='foreignkey')
    op.drop_constraint('appointments_ibfk_3', 'appointments', type_='foreignkey')
    op.create_foreign_key(None, 'appointments', 'professionals', ['professional_id'], ['id'], ondelete='SET NULL')
    op.create_foreign_key(None, 'appointments', 'services', ['service_id'], ['id'], ondelete='SET NULL')
    op.create_foreign_key(None, 'appointments', 'clients', ['client_id'], ['id'], ondelete='SET NULL')
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'appointments', type_='foreignkey')
    op.drop_constraint(None, 'appointments', type_='foreignkey')
    op.drop_constraint(None, 'appointments', type_='foreignkey')
    op.create_foreign_key('appointments_ibfk_3', 'appointments', 'services', ['service_id'], ['id'])
    op.create_foreign_key('appointments_ibfk_2', 'appointments', 'professionals', ['professional_id'], ['id'])
    op.create_foreign_key('appointments_ibfk_1', 'appointments', 'clients', ['client_id'], ['id'])
    op.alter_column('appointments', 'professional_id',
               existing_type=mysql.INTEGER(),
               nullable=False)
    op.alter_column('appointments', 'service_id',
               existing_type=mysql.INTEGER(),
               nullable=False)
    op.alter_column('appointments', 'client_id',
               existing_type=mysql.INTEGER(),
               nullable=False)
    # ### end Alembic commands ###
