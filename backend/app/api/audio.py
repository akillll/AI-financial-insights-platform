from fastapi import APIRouter, UploadFile, Depends
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.services.audio_service import (
    AudioConfirmPayload,
    ExtractResponse,
    extract_audio,
    confirm_audio,
)

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/audio/{household_id}/extract", response_model=ExtractResponse)
def upload_audio(
    household_id: int,
    file: UploadFile,
    db: Session = Depends(get_db)
):
    """
    Step 1: Transcribe audio, extract structured data, and save to DB as a draft.

    Returns the saved DB state with primary keys for every created entity
    (member_id, account.id, beneficiary.id, etc.).

    The frontend must render this response — not the raw extraction JSON —
    so that every field the advisor edits already has its DB id attached.
    """
    return extract_audio(file, household_id, db)


@router.put("/audio/{household_id}/confirm")
def confirm_audio_extraction(
    household_id: int,
    data: AudioConfirmPayload,
    db: Session = Depends(get_db)
):
    """
    Step 2: Advisor has reviewed (and optionally edited) the extracted data.

    Updates existing records by primary key — no new records are created
    unless the advisor explicitly added something (id omitted in payload).

    The frontend must send back the IDs it received from /extract.
    """
    return confirm_audio(data, household_id, db)