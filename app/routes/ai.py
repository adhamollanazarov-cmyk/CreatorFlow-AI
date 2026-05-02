from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models import Channel, ContentCalendar, ContentIdea, Script, SeoAsset
from app.responses import api_response
from app.schemas import (
    APIEnvelope,
    AnalyzeChannelRequest,
    GenerateIdeasRequest,
    GenerateIdeasResponse,
    GenerateScriptRequest,
    GenerateScriptResponse,
    GenerateSeoRequest,
    GenerateSeoResponse,
)
from app.services.ai_service import GroqAIService

router = APIRouter(prefix="/ai")


def _safe_int(value, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _safe_list_of_str(value) -> list[str]:
    if isinstance(value, list):
        return [str(item) for item in value]
    if isinstance(value, str):
        return [value]
    return []


def _get_channel_for_demo_user(db: Session, channel_id: int) -> Channel:
    channel = (
        db.query(Channel)
        .filter(Channel.id == channel_id, Channel.user_id == settings.demo_user_id)
        .first()
    )
    if not channel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Channel not found",
        )
    return channel


def _get_idea_for_demo_user(db: Session, *, idea_id: int, channel_id: int) -> ContentIdea:
    idea = (
        db.query(ContentIdea)
        .filter(
            ContentIdea.id == idea_id,
            ContentIdea.channel_id == channel_id,
            ContentIdea.user_id == settings.demo_user_id,
        )
        .first()
    )
    if not idea:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content idea not found for this channel",
        )
    return idea


def _get_script_for_demo_user(db: Session, *, script_id: int, channel_id: int) -> Script:
    script = (
        db.query(Script)
        .filter(
            Script.id == script_id,
            Script.channel_id == channel_id,
            Script.user_id == settings.demo_user_id,
        )
        .first()
    )
    if not script:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Script not found for this channel",
        )
    return script


@router.post("/generate-ideas", response_model=APIEnvelope)
async def generate_ideas(payload: GenerateIdeasRequest, db: Session = Depends(get_db)):
    channel = _get_channel_for_demo_user(db, payload.channel_id)
    ai = GroqAIService()
    generated = await ai.generate_ideas(
        channel_name=channel.name,
        niche=channel.niche,
        topic=payload.topic,
        count=payload.count,
    )

    idea_rows: list[ContentIdea] = []
    for item in generated.get("ideas", []):
        row = ContentIdea(
            user_id=settings.demo_user_id,
            channel_id=channel.id,
            title=item.get("title", "Untitled idea"),
            hook=item.get("hook", ""),
            angle=item.get("angle", ""),
            estimated_virality_score=_safe_int(item.get("estimated_virality_score", 60), 60),
            status="new",
        )
        db.add(row)
        db.flush()
        idea_rows.append(row)

    if idea_rows:
        # Minimal auto-calendar suggestion for MVP previews.
        for index, idea in enumerate(idea_rows, start=1):
            calendar = ContentCalendar(
                user_id=settings.demo_user_id,
                channel_id=channel.id,
                content_idea_id=idea.id,
                publish_date=(datetime.now(timezone.utc).date() + timedelta(days=index)),
                platform="youtube_shorts",
                status="planned",
                notes="Auto-scheduled after idea generation.",
            )
            db.add(calendar)

    db.commit()
    for row in idea_rows:
        db.refresh(row)

    response = GenerateIdeasResponse(
        channel_id=channel.id,
        ideas=[
            {
                "title": i.title,
                "hook": i.hook,
                "angle": i.angle,
                "estimated_virality_score": i.estimated_virality_score or 60,
            }
            for i in idea_rows
        ],
        model_used=ai.model,
        used_fallback=bool(generated.get("_used_fallback", False)),
    )
    return api_response(message="Ideas generated", data=response.model_dump())


@router.post("/generate-script", response_model=APIEnvelope)
async def generate_script(payload: GenerateScriptRequest, db: Session = Depends(get_db)):
    channel = _get_channel_for_demo_user(db, payload.channel_id)
    if payload.content_idea_id:
        _get_idea_for_demo_user(db, idea_id=payload.content_idea_id, channel_id=channel.id)

    ai = GroqAIService()

    generated = await ai.generate_script(
        channel_name=channel.name,
        idea_title=payload.idea_title,
        idea_hook=payload.hook,
        target_duration_seconds=payload.duration_seconds,
        style=payload.style,
        target_audience=payload.target_audience,
    )

    script_row = Script(
        user_id=settings.demo_user_id,
        channel_id=channel.id,
        content_idea_id=payload.content_idea_id,
        script_text=generated.get("script_text", ""),
        cta=generated.get("cta", ""),
        estimated_duration_seconds=_safe_int(
            generated.get("estimated_duration_seconds", payload.duration_seconds),
            payload.duration_seconds,
        ),
    )
    db.add(script_row)
    db.commit()
    db.refresh(script_row)

    response = GenerateScriptResponse(
        channel_id=channel.id,
        script_id=script_row.id,
        script_text=script_row.script_text,
        cta=script_row.cta,
        estimated_duration_seconds=script_row.estimated_duration_seconds,
        used_fallback=bool(generated.get("_used_fallback", False)),
    )
    return api_response(message="Script generated", data=response.model_dump())


@router.post("/generate-seo", response_model=APIEnvelope)
async def generate_seo(payload: GenerateSeoRequest, db: Session = Depends(get_db)):
    channel = _get_channel_for_demo_user(db, payload.channel_id)
    if payload.script_id:
        _get_script_for_demo_user(db, script_id=payload.script_id, channel_id=channel.id)

    ai = GroqAIService()
    generated = await ai.generate_seo(
        channel_name=channel.name,
        script_text=payload.script_text,
        title=payload.title,
        target_keywords=payload.target_keywords,
        platform=payload.platform,
    )

    seo_row = SeoAsset(
        user_id=settings.demo_user_id,
        channel_id=channel.id,
        script_id=payload.script_id,
        title=generated.get("title", ""),
        description=generated.get("description", ""),
        hashtags=_safe_list_of_str(generated.get("hashtags", [])),
        tags=_safe_list_of_str(generated.get("tags", [])),
        pinned_comment=generated.get("pinned_comment", ""),
    )
    db.add(seo_row)
    db.commit()
    db.refresh(seo_row)

    response = GenerateSeoResponse(
        channel_id=channel.id,
        seo_asset_id=seo_row.id,
        title=seo_row.title,
        description=seo_row.description,
        hashtags=seo_row.hashtags,
        tags=seo_row.tags,
        pinned_comment=seo_row.pinned_comment,
        used_fallback=bool(generated.get("_used_fallback", False)),
    )
    return api_response(message="SEO assets generated", data=response.model_dump())


@router.post("/analyze-channel", response_model=APIEnvelope)
async def analyze_channel(payload: AnalyzeChannelRequest, db: Session = Depends(get_db)):
    channel = _get_channel_for_demo_user(db, payload.channel_id)
    ai = GroqAIService()
    generated = await ai.analyze_channel(
        channel_name=channel.name,
        niche=channel.niche,
        context=payload.recent_context,
    )

    channel.analysis_payload = {
        "summary": generated.get("summary", ""),
        "strengths": generated.get("strengths", []),
        "opportunities": generated.get("opportunities", []),
        "content_pillars": generated.get("content_pillars", []),
        "next_actions": generated.get("next_actions", []),
    }
    channel.last_analyzed_at = datetime.now(timezone.utc)
    db.add(channel)
    db.commit()

    return api_response(
        message="Channel analyzed",
        data={
            "channel_id": channel.id,
            "analysis": channel.analysis_payload,
            "used_fallback": bool(generated.get("_used_fallback", False)),
        },
    )
