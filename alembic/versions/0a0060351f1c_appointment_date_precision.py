"""Appointment_date_precision

Revision ID: 0a0060351f1c
Revises: d9861d2cc2b8
Create Date: 2025-03-24 14:30:03.950455

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = '0a0060351f1c'
down_revision: Union[str, None] = 'd9861d2cc2b8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('appointments', 'start_time',
               existing_type=mysql.TIMESTAMP(),
               type_=mysql.DATETIME(timezone=True, fsp=6),
               existing_nullable=False)
    op.alter_column('appointments', 'end_time',
               existing_type=mysql.TIMESTAMP(),
               type_=mysql.DATETIME(timezone=True, fsp=6),
               existing_nullable=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('appointments', 'end_time',
               existing_type=mysql.DATETIME(timezone=True, fsp=6),
               type_=mysql.TIMESTAMP(),
               existing_nullable=False)
    op.alter_column('appointments', 'start_time',
               existing_type=mysql.DATETIME(timezone=True, fsp=6),
               type_=mysql.TIMESTAMP(),
               existing_nullable=False)
    # ### end Alembic commands ###
