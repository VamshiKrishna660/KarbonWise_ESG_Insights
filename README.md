# KarbonWise ESG Data Insights 🌿

An AI-powered ESG (Environmental, Social, Governance) data extraction and analysis platform. This project automates the extraction of structured sustainability metrics from complex PDF and Excel reports using LLMs.

![Frontend Dashboard Dashboard](file:///d:/Vamshi/KarbonWise_Prep/Assignment_karbonwise/FrontendUI.jpeg)

## 🚀 Overview
KarbonWise solves the unstructured data bottleneck in sustainability reporting. It transforms messy, multi-page corporate reports into a standardized, queryable database, allowing for instant analysis and trend identification.

### Key Features
- **Intelligent Extraction**: Uses **Google Gemini 2.5 Flash** to "read" and extract Scope 1/2 emissions, energy usage, and water consumption.
- **Unit Normalization**: Automatically converts diverse units (GWh, GJ, Litres, tonnes) into standard MWh and metric tonnes.
- **Interactive Dashboard**: A modern, responsive UI to upload files, filter records, and view AI-generated portfolio insights.
- **API Documentation**: Auto-generated Swagger UI for easy integration.

## 🛠️ Tech Stack
- **Backend**: FastAPI (Python)
- **Database**: SQLite with SQLAlchemy ORM
- **Migrations**: Alembic
- **LLM**: Google Gemini 2.5 Flash
- **Frontend**: Vanilla HTML5, CSS3 (Glassmorphism), and JavaScript
- **AI Tooling**: This project was built with the assistance of **Antigravity AI** (Google DeepMind).

## ⚙️ Design Decisions
- **Relational Schema**: Data is normalized into `documents` and `sustainability_records` to handle multiple reporting years per document.
- **Stateless Extraction**: The LLM prompt is engineered to handle massive context (up to 100k characters) to ensure data-heavy appendices are processed.
- **Security**: Simple but effective API Key authentication (`X-API-Key`) for backend-to-backend communication.

## 🏁 Getting Started

### 1. Setup Environment
```bash
# Create and activate venv
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Settings
Create a `.env` file in the root:
```env
GEMINI_API_KEY=your_google_ai_studio_key
API_KEY=testkey
DATABASE_URL=sqlite:///./karbonwise.db
```

### 3. Initialize Database & Seed
```bash
alembic upgrade head
python seed.py
```

### 4. Run Application
```bash
uvicorn app.main:app --reload
```
- **Dashboard**: [http://localhost:8000/](http://localhost:8000/)
- **API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)

## 📂 Deliverables Included
- [x] **Working API**: Fully functional locally.
- [x] **Documentation**: Auto-generated Swagger UI.
- [x] **Migrations**: Alembic setup with `karbonwise.db`.
- [x] **Sample Data**: 2 seeded records + script.
- [x] **Sample Files**: Test PDF and Excel files in `sample_files/`.
