from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
import os

class ReportService:
    @staticmethod
    def generate_pdf(analysis_result: dict, output_path: str):
        doc = SimpleDocTemplate(output_path, pagesize=letter)
        styles = getSampleStyleSheet()
        elements = []

        # Title
        elements.append(Paragraph(f"Market Analysis Report: {analysis_result['symbol']}", styles['Title']))
        elements.append(Spacer(1, 12))

        # Metadata
        elements.append(Paragraph(f"Generated on: {analysis_result['timestamp']}", styles['Normal']))
        elements.append(Paragraph(f"Developed by: Engineer Salah Al-Wafi", styles['Normal']))
        elements.append(Spacer(1, 24))

        # Technical Indicators Table
        data = [
            ['Indicator', 'Value'],
            ['Current Price', f"${analysis_result['current_price']:.2f}"],
            ['RSI (14)', f"{analysis_result['rsi']:.2f}"],
            ['SMA (20)', f"${analysis_result['sma_20']:.2f}"],
            ['SMA (50)', f"${analysis_result['sma_50']:.2f}"],
            ['Market Trend', analysis_result['trend']]
        ]
        
        t = Table(data, colWidths=[150, 150])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(t)
        elements.append(Spacer(1, 24))

        # AI Summary
        elements.append(Paragraph("AI-Powered Market Summary", styles['Heading2']))
        elements.append(Paragraph(analysis_result['ai_summary'], styles['Normal']))

        doc.build(elements)
        return output_path
