from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator


class CreatorFlowBaseModel(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class ChannelCreate(CreatorFlowBaseModel):
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
        json_schema_extra={
            "example": {
                "name": "CreatorFlow Lab",
                "platform": "youtube",
                "niche": "AI creator tools",
                "audience": "US",
                "tone": "dramatic",
                "content_type": "shorts",
                "youtube_handle": "@creatorflowlab",
                "language": "en",
                "about": "Shorts about practical AI automation for creators.",
            }
        },
    )

    name: str = Field(..., min_length=2, max_length=160)
    platform: str = Field(default="youtube", min_length=2, max_length=40)
    niche: str = Field(..., min_length=2, max_length=120)
    audience: str = Field(default="US", min_length=2, max_length=120)
    tone: str = Field(default="dramatic", min_length=2, max_length=80)
    content_type: str = Field(default="shorts", min_length=2, max_length=80)
    youtube_handle: str | None = Field(default=None, max_length=150)
    language: str = Field(default="en", min_length=2, max_length=40)
    about: str | None = Field(default=None, max_length=2000)


class ChannelResponse(BaseModel):
    id: int
    user_id: int
    name: str
    platform: str
    niche: str
    audience: str
    tone: str
    content_type: str
    youtube_handle: str | None
    language: str
    about: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class IdeaItem(CreatorFlowBaseModel):
    title: str = Field(..., min_length=3, max_length=220)
    hook: str = Field(..., min_length=3, max_length=1000)
    angle: str = Field(..., min_length=3, max_length=1000)
    estimated_virality_score: int = Field(default=60, ge=0, le=100)


class GenerateIdeasRequest(CreatorFlowBaseModel):
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
        json_schema_extra={
            "example": {
                "channel_id": 1,
                "topic": "Shorts automation",
                "count": 3,
            }
        },
    )

    channel_id: int = Field(..., ge=1)
    topic: str | None = Field(default=None, max_length=300)
    count: int = Field(default=5, ge=1, le=20)


class GenerateIdeasResponse(BaseModel):
    channel_id: int
    ideas: list[IdeaItem]
    model_used: str | None = None
    used_fallback: bool = False


class GenerateScriptRequest(CreatorFlowBaseModel):
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "channel_id": 1,
                "idea_title": "3 AI Shorts Automation Mistakes",
                "hook": "Most creators automate the wrong step first.",
                "duration_seconds": 30,
                "style": "fast-paced",
                "target_audience": "solo YouTube creators",
            }
        },
    )

    channel_id: int = Field(..., ge=1)
    content_idea_id: int | None = Field(default=None, ge=1)
    idea_title: str = Field(..., min_length=3, max_length=220)
    hook: str | None = Field(default=None, max_length=1000)
    duration_seconds: int = Field(default=30, ge=10, le=90)
    style: str | None = Field(default=None, max_length=120)
    target_audience: str | None = Field(default=None, max_length=200)

    @model_validator(mode="before")
    @classmethod
    def support_legacy_script_fields(cls, data):
        if isinstance(data, dict):
            if "hook" not in data and "idea_hook" in data:
                data["hook"] = data.pop("idea_hook")
            if "duration_seconds" not in data and "target_duration_seconds" in data:
                data["duration_seconds"] = data.pop("target_duration_seconds")
        return data


class GenerateScriptResponse(BaseModel):
    channel_id: int
    script_id: int | None = None
    script_text: str
    cta: str
    estimated_duration_seconds: int
    used_fallback: bool = False


class GenerateSeoRequest(CreatorFlowBaseModel):
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "channel_id": 1,
                "script_text": "Stop scrolling. Here is the simple CreatorFlow AI workflow that turns one idea into a Shorts script, SEO title, hashtags, and a content calendar.",
                "title": "AI Shorts Automation Workflow",
                "script_id": 1,
                "target_keywords": ["youtube shorts automation", "ai creator tools"],
                "platform": "youtube",
            }
        },
    )

    channel_id: int = Field(..., ge=1)
    script_id: int | None = Field(default=None, ge=1)
    script_text: str = Field(..., min_length=10, max_length=8000)
    title: str | None = Field(default=None, max_length=220)
    target_keywords: list[str] = Field(default_factory=list, max_length=25)
    platform: str = Field(default="youtube", min_length=2, max_length=40)

    @model_validator(mode="before")
    @classmethod
    def support_legacy_seo_title(cls, data):
        if isinstance(data, dict) and "title" not in data and "idea_title" in data:
            data["title"] = data.pop("idea_title")
        return data


class GenerateSeoResponse(BaseModel):
    channel_id: int
    seo_asset_id: int | None = None
    title: str
    description: str
    hashtags: list[str]
    tags: list[str]
    pinned_comment: str
    used_fallback: bool = False


class AnalyzeChannelRequest(CreatorFlowBaseModel):
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
        json_schema_extra={
            "example": {
                "channel_id": 1,
                "recent_context": "New creator channel focused on AI Shorts workflows.",
            }
        },
    )

    channel_id: int = Field(..., ge=1)
    recent_context: str | None = Field(default=None, max_length=4000)


class AnalyzeChannelResponse(BaseModel):
    channel_id: int
    analysis: dict[str, Any]
    used_fallback: bool = False


class HistoryItem(BaseModel):
    type: str
    id: int
    channel_id: int
    channel_name: str
    primary_text: str
    secondary_text: str
    created_at: str
    payload: dict[str, Any]


class HistoryResponse(BaseModel):
    user_id: int
    items: list[HistoryItem]


class APIEnvelope(BaseModel):
    success: bool = True
    message: str
    data: dict[str, Any]


class AIContentIdeasPayload(CreatorFlowBaseModel):
    ideas: list[IdeaItem] = Field(..., min_length=1, max_length=20)


class AIScriptPayload(CreatorFlowBaseModel):
    script_text: str = Field(..., min_length=10, max_length=8000)
    cta: str = Field(..., min_length=2, max_length=500)
    estimated_duration_seconds: int = Field(..., ge=10, le=90)


class AISeoPayload(CreatorFlowBaseModel):
    title: str = Field(..., min_length=3, max_length=220)
    description: str = Field(..., min_length=10, max_length=5000)
    hashtags: list[str] = Field(default_factory=list, max_length=30)
    tags: list[str] = Field(default_factory=list, max_length=50)
    pinned_comment: str = Field(..., min_length=2, max_length=1000)


class AIChannelAnalysisPayload(CreatorFlowBaseModel):
    summary: str = Field(..., min_length=10, max_length=3000)
    strengths: list[str] = Field(default_factory=list, max_length=20)
    opportunities: list[str] = Field(default_factory=list, max_length=20)
    content_pillars: list[str] = Field(default_factory=list, max_length=20)
    next_actions: list[str] = Field(default_factory=list, max_length=20)


class CalendarItemResponse(BaseModel):
    id: int
    channel_id: int
    publish_date: date
    platform: str
    status: str
    notes: str | None

    model_config = ConfigDict(from_attributes=True)
