from fastapi import APIRouter, UploadFile, File, Depends
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.services.excel_service import process_excel

router = APIRouter()

# DB dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/upload/excel")
def upload_excel(file: UploadFile = File(...), db: Session = Depends(get_db)):
    result = process_excel(file, db)
    return {"message": "Excel processed", "data": result}