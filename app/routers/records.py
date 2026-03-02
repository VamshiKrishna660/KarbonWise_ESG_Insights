"""
Router: GET /records — list with filters/pagination
         GET /records/{id} — single record detail
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.auth import require_api_key
from app.database import get_db
from app.models import SustainabilityRecord
from app.schemas import PaginatedRecords, SustainabilityRecordOut, SustainabilityRecordSummary

router = APIRouter(prefix="/records", tags=["Records"])


@router.get(
    "",
    response_model=PaginatedRecords,
    summary="List and filter sustainability records",
)
def list_records(
    company_name: Optional[str] = Query(None, description="Filter by company name (partial match)"),
    report_year: Optional[int] = Query(None, description="Filter by report year"),
    min_emissions: Optional[float] = Query(None, description="Minimum CO₂ emissions (tonnes)"),
    max_emissions: Optional[float] = Query(None, description="Maximum CO₂ emissions (tonnes)"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Records per page"),
    db: Session = Depends(get_db),
    _: str = Depends(require_api_key),
):
    """
    Return a paginated list of sustainability records with optional filters.
    """
    query = db.query(SustainabilityRecord)

    if company_name:
        query = query.filter(SustainabilityRecord.company_name.ilike(f"%{company_name}%"))
    if report_year:
        query = query.filter(SustainabilityRecord.report_year == report_year)
    if min_emissions is not None:
        query = query.filter(SustainabilityRecord.emissions_co2_tonnes >= min_emissions)
    if max_emissions is not None:
        query = query.filter(SustainabilityRecord.emissions_co2_tonnes <= max_emissions)

    total = query.count()
    results = query.offset((page - 1) * page_size).limit(page_size).all()

    return PaginatedRecords(
        total=total,
        page=page,
        page_size=page_size,
        results=results,
    )


@router.get(
    "/{record_id}",
    response_model=SustainabilityRecordOut,
    summary="Get full detail of a single sustainability record",
)
def get_record(
    record_id: int,
    db: Session = Depends(get_db),
    _: str = Depends(require_api_key),
):
    """
    Return all fields of a single sustainability record, including its source document metadata.
    """
    record = db.query(SustainabilityRecord).filter(SustainabilityRecord.id == record_id).first()
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Record with id={record_id} not found.",
        )
    return record
