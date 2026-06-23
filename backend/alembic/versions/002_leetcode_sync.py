"""Add LeetCode sync fields

Revision ID: 002
Revises: 001
Create Date: 2026-06-23
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("leetcode_username", sa.String(100), nullable=True))
    op.create_index("ix_users_leetcode_username", "users", ["leetcode_username"])

    op.add_column("user_stats", sa.Column("leetcode_ranking", sa.Integer(), nullable=True))
    op.add_column("user_stats", sa.Column("leetcode_easy", sa.Integer(), server_default="0"))
    op.add_column("user_stats", sa.Column("leetcode_medium", sa.Integer(), server_default="0"))
    op.add_column("user_stats", sa.Column("leetcode_hard", sa.Integer(), server_default="0"))
    op.add_column("user_stats", sa.Column("leetcode_contest_attended", sa.Integer(), server_default="0"))
    op.add_column("user_stats", sa.Column("leetcode_last_synced", sa.DateTime(timezone=True), nullable=True))
    op.add_column("user_stats", sa.Column("leetcode_sync_data", postgresql.JSON(astext_type=sa.Text()), nullable=True))


def downgrade() -> None:
    op.drop_column("user_stats", "leetcode_sync_data")
    op.drop_column("user_stats", "leetcode_last_synced")
    op.drop_column("user_stats", "leetcode_contest_attended")
    op.drop_column("user_stats", "leetcode_hard")
    op.drop_column("user_stats", "leetcode_medium")
    op.drop_column("user_stats", "leetcode_easy")
    op.drop_column("user_stats", "leetcode_ranking")
    op.drop_index("ix_users_leetcode_username", table_name="users")
    op.drop_column("users", "leetcode_username")