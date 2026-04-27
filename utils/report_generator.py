from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from datetime import datetime

def generate_pdf_report(output_path, paper_name, scores, keywords, grammar_issues):
    c = canvas.Canvas(output_path, pagesize=letter)
    width, height = letter
    c.setFont("Helvetica-Bold", 18)
    c.drawString(50, height - 50, "📄 Academic Paper Analysis Report")

    c.setFont("Helvetica", 12)
    c.drawString(50, height - 80, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    c.drawString(50, height - 100, f"Paper: {paper_name}")

    # Scores
    y = height - 140
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "📊 Scores:")
    c.setFont("Helvetica", 12)
    y -= 20
    for label, score in scores.items():
        c.drawString(60, y, f"{label}: {score}")
        y -= 20

    # Keywords
    y -= 10
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "🔑 Top Keywords:")
    c.setFont("Helvetica", 12)
    y -= 20
    for kw in keywords:
        c.drawString(60, y, f"- {kw}")
        y -= 15
        if y < 100:
            c.showPage()
            y = height - 50

    # Grammar Issues
    y -= 10
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "📝 Grammar Issues:")
    c.setFont("Helvetica", 12)
    y -= 20
    if not grammar_issues:
        c.drawString(60, y, "✅ No grammar issues found.")
    else:
        for issue in grammar_issues:
            if y < 100:
                c.showPage()
                y = height - 50
            error = issue["error"]
            suggestion = ", ".join(issue["suggestion"]) if issue["suggestion"] else "No suggestion"
            c.drawString(60, y, f"- {error} → Suggestion: {suggestion}")
            y -= 15

    c.save()
