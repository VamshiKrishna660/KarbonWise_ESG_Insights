from __future__ import annotations
import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


# ── Document schemas ────────────────────────────────────────────────────────

class DocumentOut(BaseModel):
    id: int
    filename: str
    file_type: str
    uploaded_at: datetime.datetime

    model_config = {"from_attributes": True}


# ── Sustainability Record schemas ───────────────────────────────────────────

class SustainabilityRecordOut(BaseModel):
    id: int
    document_id: int
    company_name: Optional[str] = None
    report_year: Optional[int] = None
    emissions_co2_tonnes: Optional[float] = None
    energy_usage_mwh: Optional[float] = None
    water_usage_m3: Optional[float] = None
    sustainability_targets: Optional[str] = None
    raw_text_excerpt: Optional[str] = None
    confidence_score: Optional[float] = None
    created_at: datetime.datetime
    document: DocumentOut

    model_config = {"from_attributes": True}


class SustainabilityRecordSummary(BaseModel):
    """Lightweight version for list endpoints."""
    id: int
    document_id: int
    company_name: Optional[str] = None
    report_year: Optional[int] = None
    emissions_co2_tonnes: Optional[float] = None
    energy_usage_mwh: Optional[float] = None
    water_usage_m3: Optional[float] = None
    confidence_score: Optional[float] = None

    model_config = {"from_attributes": True}


# ── Upload response ─────────────────────────────────────────────────────────

class UploadResponse(BaseModel):
    message: str
    document: DocumentOut
    record: SustainabilityRecordOut


# ── Paginated list response ─────────────────────────────────────────────────

class PaginatedRecords(BaseModel):
    total: int
    page: int
    page_size: int
    results: List[SustainabilityRecordSummary]


# ── Insights response ───────────────────────────────────────────────────────

class InsightsResponse(BaseModel):
    summary: str
    record_count: int
    avg_emissions_co2_tonnes: Optional[float] = None
    avg_energy_usage_mwh: Optional[float] = None
    avg_water_usage_m3: Optional[float] = None
