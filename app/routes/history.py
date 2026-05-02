from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models import Channel, ContentIdea, Script, SeoAsset
from app.responses import api_response
from app.schemas import APIEnvelope

router = APIRouter(prefix="/history")


@router.get("", response_model=APIEnvelope)
def get_history(limit: int = Query(default=50, ge=1, le=500), db: Session = Depends(get_db)):
    channels = (
        db.query(Channel)
        .filter(Channel.user_id == settings.demo_user_id)
        .all()
    )
    channel_names = {channel.id: channel.name for channel in channels}

    ideas = (
        db.query(ContentIdea)
        .filter(ContentIdea.user_id == settings.demo_user_id)
        .order_by(ContentIdea.created_at.desc())
        .limit(limit)
        .all()
    )
    scripts = (
        db.query(Script)
        .filter(Script.user_id == settings.demo_user_id)
        .order_by(Script.created_at.desc())
        .limit(limit)
        .all()
    )
    seo_assets = (
        db.query(SeoAsset)
        .filter(SeoAsset.user_id == settings.demo_user_id)
        .order_by(SeoAsset.created_at.desc())
        .limit(limit)
        .all()
    )

    history_items = []
    for idea in ideas:
        history_items.append(
            {
                "type": "idea",
                "id": idea.id,
                "channel_id": idea.channel_id,
                "channel_name": channel_names.get(idea.channel_id, ""),
                "primary_text": idea.title,
                "secondary_text": idea.hook,
                "created_at": idea.created_at.isoformat(),
                "payload": {
                    "title": idea.title,
                    "hook": idea.hook,
                    "angle": idea.angle,
                    "estimated_virality_score": idea.estimated_virality_score,
                },
            }
        )
    for script in scripts:
        history_items.append(
            {
                "type": "script",
                "id": script.id,
                "channel_id": script.channel_id,
                "channel_name": channel_names.get(script.channel_id, ""),
                "primary_text": script.script_text,
                "secondary_text": script.cta,
                "created_at": script.created_at.isoformat(),
                "payload": {
                    "content_idea_id": script.content_idea_id,
                    "script_text": script.script_text,
                    "cta": script.cta,
                    "estimated_duration_seconds": script.estimated_duration_seconds,
                },
            }
        )
    for seo in seo_assets:
        history_items.append(
            {
                "type": "seo",
                "id": seo.id,
                "channel_id": seo.channel_id,
                "channel_name": channel_names.get(seo.channel_id, ""),
                "primary_text": seo.title,
                "secondary_text": seo.description,
                "created_at": seo.created_at.isoformat(),
                "payload": {
                    "script_id": seo.script_id,
                    "title": seo.title,
                    "description": seo.description,
                    "hashtags": seo.hashtags,
                    "tags": seo.tags,
                    "pinned_comment": seo.pinned_comment,
                },
            }
        )

    history_items.sort(key=lambda x: x["created_at"], reverse=True)
    history_items = history_items[:limit]

    return api_response(
        message="History fetched",
        data={"user_id": settings.demo_user_id, "items": history_items},
    )
