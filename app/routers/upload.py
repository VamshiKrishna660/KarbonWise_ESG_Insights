"""
Router: POST /upload
Accepts a PDF or Excel file, extracts ESG data via LLM, persists to DB.
"""
import os
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.auth import require_api_key
from app.database import get_db
from app.models import Document, SustainabilityRecord
from app.parsers import parse_pdf, parse_excel
from app.llm import extract_sustainability_data
from app.schemas import UploadResponse

router = APIRouter(prefix="/upload", tags=["Upload"])

ALLOWED_EXTENSIONS = {"pdf", "xlsx", "xls"}


@router.post(
    "",
    response_model=UploadResponse,
    status_code=status.HTTP_200_OK,
    summary="Upload a sustainability document (PDF or Excel)",
)
async def upload_document(
    file: UploadFile = File(..., description="PDF or Excel sustainability report"),
    db: Session = Depends(get_db),
    _: str = Depends(require_api_key),
):
    """
    Upload a PDF or Excel file containing sustainability data.
    The file content is parsed, sent to Gemini for structured extraction,
    and the results are stored in the database.
    """
    # Validate file extension
    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Unsupported file type '.{ext}'. Allowed: pdf, xlsx, xls",
        )

    file_bytes = await file.read()
    if len(file_bytes) == 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Uploaded file is empty.",
        )

    # Parse raw text from file
    try:
        if ext == "pdf":
            raw_text = parse_pdf(file_bytes)
            file_type = "pdf"
        else:
            raw_text = parse_excel(file_bytes)
            file_type = "xlsx"
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Failed to parse file: {str(e)}",
        )

    if not raw_text.strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No text could be extracted from the uploaded file.",
        )

    # Extract structured data via LLM
    try:
        extracted = extract_sustainability_data(raw_text)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"LLM extraction failed: {str(e)}",
        )

    # Persist document metadata
    doc = Document(filename=file.filename, file_type=file_type)
    db.add(doc)
    db.flush()  # get doc.id before committing

    # Persist extraction results
    record = SustainabilityRecord(
        document_id=doc.id,
        company_name=extracted.get("company_name"),
        report_year=extracted.get("report_year"),
        emissions_co2_tonnes=extracted.get("emissions_co2_tonnes"),
        energy_usage_mwh=extracted.get("energy_usage_mwh"),
        water_usage_m3=extracted.get("water_usage_m3"),
        sustainability_targets=extracted.get("sustainability_targets"),
        raw_text_excerpt=raw_text[:2000],  # store first 2000 chars as excerpt
        confidence_score=extracted.get("confidence_score"),
    )
    db.add(record)
    db.commit()
    db.refresh(doc)
    db.refresh(record)

    return UploadResponse(
        message="File uploaded and processed successfully.",
        document=doc,
        record=record,
    )
