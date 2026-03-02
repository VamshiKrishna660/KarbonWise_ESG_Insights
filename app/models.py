import datetime
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Document(Base):
    """Represents an uploaded file (PDF or Excel)."""
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    file_type = Column(String(10), nullable=False)  # "pdf" or "xlsx"
    uploaded_at = Column(DateTime, default=datetime.datetime.utcnow)

    records = relationship("SustainabilityRecord", back_populates="document", cascade="all, delete-orphan")


class SustainabilityRecord(Base):
    """Extracted sustainability fields from a document."""
    __tablename__ = "sustainability_records"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)

    company_name = Column(String(255), nullable=True)
    report_year = Column(Integer, nullable=True)
    emissions_co2_tonnes = Column(Float, nullable=True)
    energy_usage_mwh = Column(Float, nullable=True)
    water_usage_m3 = Column(Float, nullable=True)
    sustainability_targets = Column(Text, nullable=True)
    raw_text_excerpt = Column(Text, nullable=True)
    confidence_score = Column(Float, nullable=True)  # 0.0 – 1.0

    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    document = relationship("Document", back_populates="records")
