# KarbonWise ESG Data Extraction API

A REST API that ingests sustainability documents (PDF or Excel), extracts structured ESG metrics using **Google Gemini 2.5 Flash**, persists them in a relational database, and exposes query + insight endpoints.

---

## Quick Start

### 1. Prerequisites
- Python 3.11+
- A Google Gemini API key → [Get one free at Google AI Studio](https://aistudio.google.com/)

### 2. Clone & Setup

```powershell
# Activate the virtualenv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment

```powershell
# Copy the template
copy .env.example .env
```

Edit `.env` and fill in your values:
```
GEMINI_API_KEY=your_actual_gemini_api_key
API_KEY=testkey        # used as X-API-Key header in all requests
DATABASE_URL=sqlite:///./karbonwise.db
```

### 4. Run Database Migrations

```powershell
alembic upgrade head
```

### 5. (Optional) Seed Sample Data

```powershell
python seed.py
```

### 6. Generate Sample Files for Testing

```powershell
python create_sample_files.py
# Creates: sample_files/sample_esg_report.pdf
#          sample_files/sample_esg_data.xlsx
```

### 7. Start the API

```powershell
uvicorn app.main:app --reload
```

Open **http://127.0.0.1:8000/docs** for the interactive Swagger UI.

---

## API Endpoints

All endpoints require the header: `X-API-Key: testkey` (or whatever you set in `.env`).

| Method | URL | Description |
|---|---|---|
| `GET` | `/` | Health check |
| `POST` | `/upload` | Upload PDF or Excel, extract ESG data |
| `GET` | `/records` | List records with filters & pagination |
| `GET` | `/records/{id}` | Full detail for one record |
| `GET` | `/insights` | AI-generated natural language summary |

### Filters for `GET /records`
| Parameter | Type | Description |
|---|---|---|
| `company_name` | string | Partial match (case-insensitive) |
| `report_year` | int | Exact year filter |
| `min_emissions` | float | Minimum CO₂ tonnes |
| `max_emissions` | float | Maximum CO₂ tonnes |
| `page` | int | Page number (default 1) |
| `page_size` | int | Records per page (default 10, max 100) |

---

## Testing with the Sample Files

```powershell
# Upload the sample PDF
curl -X POST http://127.0.0.1:8000/upload \
  -H "X-API-Key: testkey" \
  -F "file=@sample_files/sample_esg_report.pdf"

# Upload the sample Excel
curl -X POST http://127.0.0.1:8000/upload \
  -H "X-API-Key: testkey" \
  -F "file=@sample_files/sample_esg_data.xlsx"

# List all records
curl http://127.0.0.1:8000/records -H "X-API-Key: testkey"

# Get insights summary
curl http://127.0.0.1:8000/insights -H "X-API-Key: testkey"
```

---

## Design Decisions

### LLM: Google Gemini 2.5 Flash
Gemini 2.5 Flash was chosen for its strong instruction-following on structured JSON extraction tasks, fast response time, and generous free tier. The extraction prompt explicitly instructs the model to return only a JSON object with null for missing fields and a confidence score — making the response predictable and easy to parse robustly.

### Database: SQLite (PostgreSQL-ready)
SQLite is used for local development simplicity. The SQLAlchemy abstraction means swapping to PostgreSQL requires only a one-line change to `DATABASE_URL` in `.env`. Schema migrations are managed by **Alembic** for reproducibility.

### Schema Design
Two tables with a 1-to-many relationship:
- **`documents`** — upload metadata (filename, type, timestamp)
- **`sustainability_records`** — extracted ESG fields linked to a document

This separation allows future support for extracting multiple records per document (e.g., multi-year reports).

### Auth
A simple static API key (`X-API-Key` header) is used — appropriate for a backend service that would typically sit behind an API gateway or be called by internal services. Full JWT user management was intentionally excluded to avoid over-engineering.

### File Parsing
- **PDF**: `pdfplumber` extracts both free text and tables (tables are row-joined as pipe-separated text).
- **Excel**: `pandas` reads all sheets and converts them to a text representation before passing to the LLM.

---

## AI Tools Used
This project was built with assistance from **Google Antigravity (Gemini)** for code generation and scaffolding. All design decisions were made and reviewed by the developer.
