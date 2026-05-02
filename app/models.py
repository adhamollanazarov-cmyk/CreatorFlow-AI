from datetime import date, datetime, timezone
from typing import Any

from sqlalchemy import Date, DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    )


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    display_name: Mapped[str] = mapped_column(String(120), nullable=False)

    channels: Mapped[list["Channel"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    ideas: Mapped[list["ContentIdea"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    scripts: Mapped[list["Script"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    seo_assets: Mapped[list["SeoAsset"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    calendar_items: Mapped[list["ContentCalendar"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )


class Channel(Base, TimestampMixin):
    __tablename__ = "channels"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    platform: Mapped[str] = mapped_column(String(40), nullable=False, default="youtube")
    niche: Mapped[str] = mapped_column(String(120), nullable=False)
    audience: Mapped[str] = mapped_column(String(120), nullable=False, default="US")
    tone: Mapped[str] = mapped_column(String(80), nullable=False, default="dramatic")
    content_type: Mapped[str] = mapped_column(String(80), nullable=False, default="shorts")
    youtube_handle: Mapped[str | None] = mapped_column(String(150), nullable=True)
    language: Mapped[str] = mapped_column(String(40), nullable=False, default="en")
    about: Mapped[str | None] = mapped_column(Text, nullable=True)

    analysis_payload: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    last_analyzed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    user: Mapped["User"] = relationship(back_populates="channels")
    ideas: Mapped[list["ContentIdea"]] = relationship(
        back_populates="channel",
        cascade="all, delete-orphan",
    )
    scripts: Mapped[list["Script"]] = relationship(
        back_populates="channel",
        cascade="all, delete-orphan",
    )
    seo_assets: Mapped[list["SeoAsset"]] = relationship(
        back_populates="channel",
        cascade="all, delete-orphan",
    )
    calendar_items: Mapped[list["ContentCalendar"]] = relationship(
        back_populates="channel",
        cascade="all, delete-orphan",
    )


class ContentIdea(Base, TimestampMixin):
    __tablename__ = "content_ideas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    channel_id: Mapped[int] = mapped_column(ForeignKey("channels.id", ondelete="CASCADE"), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(220), nullable=False)
    hook: Mapped[str] = mapped_column(Text, nullable=False)
    angle: Mapped[str] = mapped_column(Text, nullable=False)
    estimated_virality_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="draft")

    channel: Mapped["Channel"] = relationship(back_populates="ideas")
    user: Mapped["User"] = relationship(back_populates="ideas")
    scripts: Mapped[list["Script"]] = relationship(back_populates="content_idea")
    calendar_items: Mapped[list["ContentCalendar"]] = relationship(back_populates="content_idea")


class Script(Base, TimestampMixin):
    __tablename__ = "scripts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    channel_id: Mapped[int] = mapped_column(ForeignKey("channels.id", ondelete="CASCADE"), index=True, nullable=False)
    content_idea_id: Mapped[int | None] = mapped_column(
        ForeignKey("content_ideas.id", ondelete="SET NULL"),
        nullable=True,
    )
    script_text: Mapped[str] = mapped_column(Text, nullable=False)
    cta: Mapped[str] = mapped_column(Text, nullable=False)
    estimated_duration_seconds: Mapped[int] = mapped_column(Integer, nullable=False, default=30)

    channel: Mapped["Channel"] = relationship(back_populates="scripts")
    user: Mapped["User"] = relationship(back_populates="scripts")
    content_idea: Mapped["ContentIdea | None"] = relationship(back_populates="scripts")
    seo_assets: Mapped[list["SeoAsset"]] = relationship(back_populates="script")


class SeoAsset(Base, TimestampMixin):
    __tablename__ = "seo_assets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    channel_id: Mapped[int] = mapped_column(ForeignKey("channels.id", ondelete="CASCADE"), index=True, nullable=False)
    script_id: Mapped[int | None] = mapped_column(ForeignKey("scripts.id", ondelete="SET NULL"), nullable=True)

    title: Mapped[str] = mapped_column(String(220), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    hashtags: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    tags: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    pinned_comment: Mapped[str] = mapped_column(Text, nullable=False)

    channel: Mapped["Channel"] = relationship(back_populates="seo_assets")
    user: Mapped["User"] = relationship(back_populates="seo_assets")
    script: Mapped["Script | None"] = relationship(back_populates="seo_assets")


class ContentCalendar(Base, TimestampMixin):
    __tablename__ = "content_calendar"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    channel_id: Mapped[int] = mapped_column(ForeignKey("channels.id", ondelete="CASCADE"), index=True, nullable=False)
    content_idea_id: Mapped[int | None] = mapped_column(
        ForeignKey("content_ideas.id", ondelete="SET NULL"),
        nullable=True,
    )

    publish_date: Mapped[date] = mapped_column(Date, nullable=False)
    platform: Mapped[str] = mapped_column(String(40), nullable=False, default="youtube_shorts")
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="planned")
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    channel: Mapped["Channel"] = relationship(back_populates="calendar_items")
    user: Mapped["User"] = relationship(back_populates="calendar_items")
    content_idea: Mapped["ContentIdea | None"] = relationship(back_populates="calendar_items")
