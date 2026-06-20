"""split userid and username

Revision ID: 12d95178888c
Revises: 23cfcafba0a6
Create Date: 2026-06-20 12:06:44.139735

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "12d95178888c"
down_revision: Union[str, Sequence[str], None] = "23cfcafba0a6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # 1. Rename username to userid
    op.alter_column("users", "username", new_column_name="userid")

    # 2. Add username (display name) column as nullable first
    op.add_column("users", sa.Column("username", sa.String(length=50), nullable=True))

    # 3. Populate username with userid values
    op.execute("UPDATE users SET username = userid")

    # 4. Make username non-nullable
    op.alter_column("users", "username", nullable=False)

    # 5. Recreate unique constraint with userid name
    op.drop_constraint("users_username_key", "users", type_="unique")
    op.create_unique_constraint("users_userid_key", "users", ["userid"])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint("users_userid_key", "users", type_="unique")
    op.create_unique_constraint("users_username_key", "users", ["userid"])
    op.drop_column("users", "username")
    op.alter_column("users", "userid", new_column_name="username")
