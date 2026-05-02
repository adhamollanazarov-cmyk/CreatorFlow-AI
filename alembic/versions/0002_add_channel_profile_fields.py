"""add channel profile fields

Revision ID: 0002_add_channel_profile_fields
Revises: 0001_initial_schema
Create Date: 2026-05-03
"""
from alembic import op
import sqlalchemy as sa


revision = "0002_add_channel_profile_fields"
down_revision = "0001_initial_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("UPDATE channels SET niche = 'general' WHERE niche IS NULL")

    with op.batch_alter_table("channels") as batch_op:
        batch_op.add_column(
            sa.Column("platform", sa.String(length=40), nullable=False, server_default="youtube"),
        )
        batch_op.add_column(
            sa.Column("audience", sa.String(length=120), nullable=False, server_default="US"),
        )
        batch_op.add_column(
            sa.Column("tone", sa.String(length=80), nullable=False, server_default="dramatic"),
        )
        batch_op.add_column(
            sa.Column("content_type", sa.String(length=80), nullable=False, server_default="shorts"),
        )
        batch_op.alter_column(
            "niche",
            existing_type=sa.String(length=120),
            nullable=False,
        )
        batch_op.alter_column("platform", server_default=None)
        batch_op.alter_column("audience", server_default=None)
        batch_op.alter_column("tone", server_default=None)
        batch_op.alter_column("content_type", server_default=None)


def downgrade() -> None:
    with op.batch_alter_table("channels") as batch_op:
        batch_op.alter_column(
            "niche",
            existing_type=sa.String(length=120),
            nullable=True,
        )
        batch_op.drop_column("content_type")
        batch_op.drop_column("tone")
        batch_op.drop_column("audience")
        batch_op.drop_column("platform")
