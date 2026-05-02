from datetime import datetime, timezone
from io import BytesIO

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models import Channel
from app.services.excel_export_service import ExcelExportService

router = APIRouter(prefix="/export")


@router.get("/excel")
def export_excel(channel_id: int | None = Query(default=None), db: Session = Depends(get_db)):
    if channel_id is not None:
        channel_exists = (
            db.query(Channel.id)
            .filter(Channel.id == channel_id, Channel.user_id == settings.demo_user_id)
            .first()
        )
        if not channel_exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Channel not found",
            )

    service = ExcelExportService()
    workbook_bytes = service.build_workbook_bytes(
        db,
        user_id=settings.demo_user_id,
        channel_id=channel_id,
    )

    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    filename = f"creatorflow-export-{stamp}.xlsx"

    return StreamingResponse(
        BytesIO(workbook_bytes),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
