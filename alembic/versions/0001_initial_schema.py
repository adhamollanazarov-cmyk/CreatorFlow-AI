"""initial schema

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-05-03
"""
from alembic import op
import sqlalchemy as sa


revision = "0001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("display_name", sa.String(length=120), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)
    op.create_index(op.f("ix_users_id"), "users", ["id"], unique=False)

    op.create_table(
        "channels",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("niche", sa.String(length=120), nullable=True),
        sa.Column("youtube_handle", sa.String(length=150), nullable=True),
        sa.Column("language", sa.String(length=40), nullable=False),
        sa.Column("about", sa.Text(), nullable=True),
        sa.Column("analysis_payload", sa.JSON(), nullable=True),
        sa.Column("last_analyzed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_channels_id"), "channels", ["id"], unique=False)
    op.create_index(op.f("ix_channels_user_id"), "channels", ["user_id"], unique=False)

    op.create_table(
        "content_ideas",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("channel_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=220), nullable=False),
        sa.Column("hook", sa.Text(), nullable=False),
        sa.Column("angle", sa.Text(), nullable=False),
        sa.Column("estimated_virality_score", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["channel_id"], ["channels.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_content_ideas_channel_id"), "content_ideas", ["channel_id"], unique=False)
    op.create_index(op.f("ix_content_ideas_id"), "content_ideas", ["id"], unique=False)
    op.create_index(op.f("ix_content_ideas_user_id"), "content_ideas", ["user_id"], unique=False)

    op.create_table(
        "scripts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("channel_id", sa.Integer(), nullable=False),
        sa.Column("content_idea_id", sa.Integer(), nullable=True),
        sa.Column("script_text", sa.Text(), nullable=False),
        sa.Column("cta", sa.Text(), nullable=False),
        sa.Column("estimated_duration_seconds", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["channel_id"], ["channels.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["content_idea_id"], ["content_ideas.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_scripts_channel_id"), "scripts", ["channel_id"], unique=False)
    op.create_index(op.f("ix_scripts_id"), "scripts", ["id"], unique=False)
    op.create_index(op.f("ix_scripts_user_id"), "scripts", ["user_id"], unique=False)

    op.create_table(
        "content_calendar",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("channel_id", sa.Integer(), nullable=False),
        sa.Column("content_idea_id", sa.Integer(), nullable=True),
        sa.Column("publish_date", sa.Date(), nullable=False),
        sa.Column("platform", sa.String(length=40), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["channel_id"], ["channels.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["content_idea_id"], ["content_ideas.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_content_calendar_channel_id"), "content_calendar", ["channel_id"], unique=False)
    op.create_index(op.f("ix_content_calendar_id"), "content_calendar", ["id"], unique=False)
    op.create_index(op.f("ix_content_calendar_user_id"), "content_calendar", ["user_id"], unique=False)

    op.create_table(
        "seo_assets",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("channel_id", sa.Integer(), nullable=False),
        sa.Column("script_id", sa.Integer(), nullable=True),
        sa.Column("title", sa.String(length=220), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("hashtags", sa.JSON(), nullable=False),
        sa.Column("tags", sa.JSON(), nullable=False),
        sa.Column("pinned_comment", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["channel_id"], ["channels.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["script_id"], ["scripts.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_seo_assets_channel_id"), "seo_assets", ["channel_id"], unique=False)
    op.create_index(op.f("ix_seo_assets_id"), "seo_assets", ["id"], unique=False)
    op.create_index(op.f("ix_seo_assets_user_id"), "seo_assets", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_seo_assets_user_id"), table_name="seo_assets")
    op.drop_index(op.f("ix_seo_assets_id"), table_name="seo_assets")
    op.drop_index(op.f("ix_seo_assets_channel_id"), table_name="seo_assets")
    op.drop_table("seo_assets")
    op.drop_index(op.f("ix_content_calendar_user_id"), table_name="content_calendar")
    op.drop_index(op.f("ix_content_calendar_id"), table_name="content_calendar")
    op.drop_index(op.f("ix_content_calendar_channel_id"), table_name="content_calendar")
    op.drop_table("content_calendar")
    op.drop_index(op.f("ix_scripts_user_id"), table_name="scripts")
    op.drop_index(op.f("ix_scripts_id"), table_name="scripts")
    op.drop_index(op.f("ix_scripts_channel_id"), table_name="scripts")
    op.drop_table("scripts")
    op.drop_index(op.f("ix_content_ideas_user_id"), table_name="content_ideas")
    op.drop_index(op.f("ix_content_ideas_id"), table_name="content_ideas")
    op.drop_index(op.f("ix_content_ideas_channel_id"), table_name="content_ideas")
    op.drop_table("content_ideas")
    op.drop_index(op.f("ix_channels_user_id"), table_name="channels")
    op.drop_index(op.f("ix_channels_id"), table_name="channels")
    op.drop_table("channels")
    op.drop_index(op.f("ix_users_id"), table_name="users")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")
