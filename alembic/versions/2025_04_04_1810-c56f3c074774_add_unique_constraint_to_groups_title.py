"""Add unique constraint to groups.title

Revision ID: c56f3c074774
Revises: 6ff07c80cc3a
Create Date: 2025-04-04 18:10:15.281786

"""

from typing import Union
from collections.abc import Sequence

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'c56f3c074774'
down_revision: Union[str, None] = '6ff07c80cc3a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('ix_groups_title', table_name='groups')
    op.create_index(op.f('ix_groups_title'), 'groups', ['title'], unique=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_groups_title'), table_name='groups')
    op.create_index('ix_groups_title', 'groups', ['title'], unique=False)
    # ### end Alembic commands ###
