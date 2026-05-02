from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models import Channel
from app.responses import api_response
from app.schemas import APIEnvelope, ChannelCreate, ChannelResponse

router = APIRouter(prefix="/channels")


@router.post("", response_model=APIEnvelope, status_code=status.HTTP_201_CREATED)
def create_channel(payload: ChannelCreate, db: Session = Depends(get_db)):
    channel = Channel(
        user_id=settings.demo_user_id,  # Temporary demo user, replaced by auth identity later.
        name=payload.name,
        platform=payload.platform,
        niche=payload.niche,
        audience=payload.audience,
        tone=payload.tone,
        content_type=payload.content_type,
        youtube_handle=payload.youtube_handle,
        language=payload.language,
        about=payload.about,
    )
    db.add(channel)
    db.commit()
    db.refresh(channel)

    return api_response(
        message="Channel created",
        data={"channel": ChannelResponse.model_validate(channel).model_dump()},
    )


@router.get("", response_model=APIEnvelope)
def list_channels(db: Session = Depends(get_db)):
    channels = (
        db.query(Channel)
        .filter(Channel.user_id == settings.demo_user_id)
        .order_by(Channel.created_at.desc())
        .all()
    )
    return api_response(
        message="Channels fetched",
        data={"channels": [ChannelResponse.model_validate(c).model_dump() for c in channels]},
    )


@router.get("/{channel_id}", response_model=APIEnvelope)
def get_channel(channel_id: int, db: Session = Depends(get_db)):
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

    return api_response(
        message="Channel fetched",
        data={"channel": ChannelResponse.model_validate(channel).model_dump()},
    )
