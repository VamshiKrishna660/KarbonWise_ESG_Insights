"""
Router: GET /insights — natural language summary from aggregated DB data.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.auth import require_api_key
from app.database import get_db
from app.models import SustainabilityRecord
from app.llm import generate_insights
from app.schemas import InsightsResponse

router = APIRouter(prefix="/insights", tags=["Insights"])


@router.get(
    "",
    response_model=InsightsResponse,
    summary="Generate a natural language ESG summary across all records",
)
def get_insights(
    db: Session = Depends(get_db),
    _: str = Depends(require_api_key),
):
    """
    Aggregates all sustainability records and generates a natural language
    summary using Gemini, highlighting trends and key metrics.
    """
    agg = db.query(
        func.count(SustainabilityRecord.id).label("count"),
        func.avg(SustainabilityRecord.emissions_co2_tonnes).label("avg_emissions"),
        func.avg(SustainabilityRecord.energy_usage_mwh).label("avg_energy"),
        func.avg(SustainabilityRecord.water_usage_m3).label("avg_water"),
        func.min(SustainabilityRecord.emissions_co2_tonnes).label("min_emissions"),
        func.max(SustainabilityRecord.emissions_co2_tonnes).label("max_emissions"),
    ).one()

    stats = {
        "total_records": agg.count,
        "avg_emissions_co2_tonnes": round(agg.avg_emissions, 2) if agg.avg_emissions else None,
        "avg_energy_usage_mwh": round(agg.avg_energy, 2) if agg.avg_energy else None,
        "avg_water_usage_m3": round(agg.avg_water, 2) if agg.avg_water else None,
        "min_emissions_co2_tonnes": agg.min_emissions,
        "max_emissions_co2_tonnes": agg.max_emissions,
    }

    # Fetch company names for richer context
    companies = db.query(SustainabilityRecord.company_name).distinct().all()
    stats["companies_tracked"] = [c[0] for c in companies if c[0]]

    summary_text = generate_insights(stats)

    return InsightsResponse(
        summary=summary_text,
        record_count=agg.count,
        avg_emissions_co2_tonnes=stats["avg_emissions_co2_tonnes"],
        avg_energy_usage_mwh=stats["avg_energy_usage_mwh"],
        avg_water_usage_m3=stats["avg_water_usage_m3"],
    )
