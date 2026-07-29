"""add_session_messages_jlpt_teaching_mode

Revision ID: eba2879c4ab9
Revises: e74b9694aa05
Create Date: 2026-07-29 18:54:08.288686

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB


# revision identifiers, used by Alembic.
revision: str = 'eba2879c4ab9'
down_revision: Union[str, None] = 'e74b9694aa05'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('sessions', sa.Column('messages', JSONB, nullable=False, server_default='[]'))
    op.add_column('sessions', sa.Column('jlpt_level', sa.String(10), nullable=False, server_default='N4'))
    op.add_column('sessions', sa.Column('teaching_mode', sa.String(20), nullable=False, server_default='bilingual'))


def downgrade() -> None:
    op.drop_column('sessions', 'teaching_mode')
    op.drop_column('sessions', 'jlpt_level')
    op.drop_column('sessions', 'messages')
