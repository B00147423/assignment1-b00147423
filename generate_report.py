import json
from reportlab.pdfgen import canvas

with open("test-results.json") as f:
    results = json.load(f)

pdf = canvas.Canvas("test-report.pdf")
pdf.drawString(100, 800, "TEST RESULTS")
y = 780

for test in results.get("tests", []):
    outcome = "PASS" if test["outcome"] == "passed" else "FAIL"
    pdf.drawString(100, y, f"{test['nodeid']}: {outcome}")
    y -= 20

pdf.save()
