"""
LLM extraction logic using Google Gemini (gemini-2.5-flash).
"""
import json
import re
from typing import Optional
import google.generativeai as genai
from app.config import get_settings

settings = get_settings()
genai.configure(api_key=settings.gemini_api_key)

_MODEL_NAME = "gemini-2.5-flash"

EXTRACTION_PROMPT = """
You are a highly detailed ESG (Environmental, Social, Governance) Data Scientist. 
Your goal is to extract specific performance metrics from a company's sustainability report.

### Extraction Instructions:
1. **Company Name**: Look for the main reporting entity (check titles, headers, and "About This Report").
2. **Report Year**: Extract the specific fiscal or calendar year this data represents (not the publication date).
3. **Emissions (tCO2e)**: 
   - Look for "Total GHG Emissions", "Scope 1 + Scope 2", or "Carbon Footprint". 
   - Ensure the unit is metric tonnes. If given in "thousand tonnes", multiply by 1,000.
   - Ignore "Intensity" metrics (emissions per revenue) if absolute totals are available.
4. **Energy (MWh)**: 
   - Look for "Total Energy Consumption" or "Total Secondary Energy". 
   - Convert GWh to MWh (multiply by 1,000) or GJ to MWh (divide by 3.6).
5. **Water (m3)**: 
   - Look for "Total Water Withdrawal" or "Water Consumption". 
   - Convert Liters/kL to cubic meters (1,000 L = 1 m3).
6. **Targets**: Summarize the most ambitious net-zero or reduction commitments.
7. **Confidence**: Rate from 0.0 to 1.0 based on how clearly these numbers were labeled.

### Output Format:
Return ONLY a valid JSON object. No markdown, no pre-amble.
{{
  "company_name": string | null,
  "report_year": integer | null,
  "emissions_co2_tonnes": float | null,
  "energy_usage_mwh": float | null,
  "water_usage_m3": float | null,
  "sustainability_targets": string | null,
  "confidence_score": float
}}

Document Text:
{text}
"""

INSIGHTS_PROMPT = """
You are an ESG data analyst. Based on the following aggregated sustainability statistics,
write a concise natural language summary (3-5 sentences) highlighting key trends,
notable figures, and any gaps in the data.

Statistics:
{stats}
"""


def extract_sustainability_data(text: str) -> dict:
    """Send document text to Gemini and return extracted fields as a dict."""
    # Increased limit to 100k chars for real reports (usually 50-100 pages)
    prompt = EXTRACTION_PROMPT.format(text=text[:100000])  
    model = genai.GenerativeModel(_MODEL_NAME)
    response = model.generate_content(prompt)
    raw = response.text.strip()

    # Strip potential markdown code fences
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        # Fallback: return empty extraction
        data = {
            "company_name": None,
            "report_year": None,
            "emissions_co2_tonnes": None,
            "energy_usage_mwh": None,
            "water_usage_m3": None,
            "sustainability_targets": None,
            "confidence_score": 0.0,
        }
    return data


def generate_insights(stats: dict) -> str:
    """Generate a natural language summary of aggregated ESG statistics."""
    stats_text = json.dumps(stats, indent=2)
    prompt = INSIGHTS_PROMPT.format(stats=stats_text)
    model = genai.GenerativeModel(_MODEL_NAME)
    response = model.generate_content(prompt)
    return response.text.strip()
