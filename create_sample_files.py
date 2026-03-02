"""
Script to generate sample PDF and Excel files for testing.
Run: python create_sample_files.py
"""
import os
import openpyxl
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "sample_files")
os.makedirs(OUTPUT_DIR, exist_ok=True)


def create_sample_pdf():
    path = os.path.join(OUTPUT_DIR, "sample_esg_report.pdf")
    doc = SimpleDocTemplate(path, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("Acme Corp — ESG & Sustainability Report 2023", styles["Title"]))
    story.append(Spacer(1, 12))
    story.append(Paragraph("Executive Summary", styles["Heading2"]))
    story.append(Paragraph(
        "Acme Corp is committed to sustainable business practices. In 2023, we made significant "
        "progress toward our climate targets, reducing greenhouse gas emissions and improving "
        "energy efficiency across all our global operations.",
        styles["Normal"]
    ))
    story.append(Spacer(1, 12))

    story.append(Paragraph("Environmental Performance Highlights", styles["Heading2"]))
    story.append(Paragraph(
        "This section summarises our key environmental metrics for the fiscal year 2023.",
        styles["Normal"]
    ))
    story.append(Spacer(1, 8))

    data = [
        ["Metric", "2023 Value", "Unit", "vs 2022"],
        ["Total GHG Emissions (Scope 1 & 2)", "12,500", "tCO₂e", "-8%"],
        ["Total Energy Consumption", "48,000", "MWh", "-5%"],
        ["Renewable Energy Share", "34", "%", "+12pp"],
        ["Water Withdrawal", "320,000", "m³", "-3%"],
        ["Waste Diverted from Landfill", "78", "%", "+4pp"],
    ]

    table = Table(data, colWidths=[200, 80, 60, 60])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2E7D32")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F1F8E9")]),
    ]))
    story.append(table)
    story.append(Spacer(1, 12))

    story.append(Paragraph("Sustainability Targets", styles["Heading2"]))
    story.append(Paragraph(
        "• Achieve net-zero GHG emissions across Scope 1, 2 and 3 by 2040.\n"
        "• Source 100% renewable electricity by 2027.\n"
        "• Reduce water intensity by 20% by 2026 (2019 baseline).\n"
        "• Zero waste to landfill from manufacturing by 2028.",
        styles["Normal"]
    ))
    story.append(Spacer(1, 12))

    story.append(Paragraph("About Acme Corp", styles["Heading2"]))
    story.append(Paragraph(
        "Acme Corp is a global manufacturing company headquartered in Hyderabad, India, "
        "with operations across 12 countries. Founded in 1998, the company employs over "
        "25,000 people and reported revenues of $4.2 billion in fiscal year 2023.",
        styles["Normal"]
    ))

    doc.build(story)
    print(f"  [OK] Created {path}")


def create_sample_excel():
    path = os.path.join(OUTPUT_DIR, "sample_esg_data.xlsx")
    wb = openpyxl.Workbook()

    # Sheet 1: Summary
    ws1 = wb.active
    ws1.title = "ESG Summary"
    ws1.append(["GreenTec Industries — ESG Data 2022"])
    ws1.append([])
    ws1.append(["Company", "GreenTec Industries"])
    ws1.append(["Report Year", 2022])
    ws1.append(["Headquarters", "Bengaluru, India"])
    ws1.append(["Employees", 8500])
    ws1.append([])
    ws1.append(["Metric", "Value", "Unit"])
    ws1.append(["CO2 Emissions (Scope 1+2)", 7800, "tonnes CO2e"])
    ws1.append(["Energy Consumption", 31500, "MWh"])
    ws1.append(["Renewable Energy", 9450, "MWh"])
    ws1.append(["Water Consumption", 185000, "m3"])
    ws1.append(["Waste Generated", 1200, "tonnes"])
    ws1.append(["Waste Recycled", 960, "tonnes"])

    # Sheet 2: Targets
    ws2 = wb.create_sheet("Targets")
    ws2.append(["Target", "Deadline", "Baseline Year", "Status"])
    ws2.append(["50% renewable energy", 2025, 2020, "On Track"])
    ws2.append(["Reduce Scope 3 emissions by 30%", 2030, 2019, "In Progress"])
    ws2.append(["Carbon neutral operations", 2035, 2020, "Planned"])
    ws2.append(["Zero liquid discharge", 2027, 2022, "In Progress"])

    wb.save(path)
    print(f"  [OK] Created {path}")


if __name__ == "__main__":
    print("Creating sample files...")
    create_sample_pdf()
    create_sample_excel()
    print("Done.")
