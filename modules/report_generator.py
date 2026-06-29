from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import os


def generate_pdf_report(report, filename="contract_report.pdf"):
    os.makedirs("reports", exist_ok=True)
    path = os.path.join("reports", filename)

    c = canvas.Canvas(path, pagesize=A4)
    width, height = A4
    y = height - 50

    def write_line(text):
        nonlocal y
        if y < 60:
            c.showPage()
            y = height - 50
        c.drawString(40, y, str(text)[:100])
        y -= 20

    write_line("LEGALMIND AI - CONTRACT ANALYSIS REPORT")
    write_line("-" * 80)

    write_line("Summary:")
    write_line(report["summary"])

    write_line("")
    write_line("Clauses Found:")
    for clause in report["found_clauses"]:
        write_line(f"- {clause}")

    write_line("")
    write_line("Missing Clauses:")
    for clause in report["missing_clauses"]:
        write_line(f"- {clause}")

    write_line("")
    write_line(f"Risk Score: {report['risk_score']}/100")
    write_line(f"Risk Level: {report['risk_level']}")

    write_line("")
    write_line("Recommendations:")
    for clause in report["missing_clauses"]:
        write_line(f"- Add proper {clause}")

    write_line("")
    write_line("Disclaimer: This is contract assistance only, not legal advice.")

    c.save()
    return path