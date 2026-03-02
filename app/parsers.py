"""
File parsers: extract raw text from PDF and Excel files.
"""
import io
import pdfplumber
import pandas as pd


def parse_pdf(file_bytes: bytes) -> str:
    """Extract all text from a PDF file."""
    text_parts = []
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
            # Also pull any tables
            for table in page.extract_tables():
                for row in table:
                    cleaned = [str(cell) if cell is not None else "" for cell in row]
                    text_parts.append(" | ".join(cleaned))
    return "\n".join(text_parts)


def parse_excel(file_bytes: bytes) -> str:
    """Convert all sheets of an Excel file to concatenated text."""
    text_parts = []
    xlsx_file = io.BytesIO(file_bytes)
    xl = pd.ExcelFile(xlsx_file)
    for sheet_name in xl.sheet_names:
        df = xl.parse(sheet_name)
        text_parts.append(f"--- Sheet: {sheet_name} ---")
        text_parts.append(df.to_string(index=False))
    return "\n".join(text_parts)
