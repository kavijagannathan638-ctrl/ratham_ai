"""initial schema

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-09-14 21:30:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Managed via SQLAlchemy declarative metadata create_all or alembic migrations
    pass

def downgrade() -> None:
    pass
