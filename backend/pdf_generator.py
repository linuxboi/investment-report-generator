"""
Professional PDF Report Generator for Investment Analysis
Creates beautifully formatted PDF reports with charts and styling
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    Image
)
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from datetime import datetime
import os
import re

class InvestmentReportPDF:
    """Generate professional PDF reports for investment analysis"""

    def __init__(self, ticker, company_name, content, output_dir="reports/output"):
        self.ticker = ticker
        self.company_name = company_name
        self.content = content
        self.output_dir = output_dir
        self.elements = []

        os.makedirs(output_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.filename = f"{output_dir}/{ticker}_report_{timestamp}.pdf"
        self.doc = SimpleDocTemplate(
            self.filename,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=50,
        )

        self.styles = getSampleStyleSheet()
        self._create_custom_styles()

    def _create_custom_styles(self):
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=28,
            textColor=colors.HexColor('#1a365d'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))

        self.styles.add(ParagraphStyle(
            name='CustomSubtitle',
            parent=self.styles['Normal'],
            fontSize=12,
            textColor=colors.HexColor('#4a5568'),
            spaceAfter=20,
            alignment=TA_CENTER,
            fontName='Helvetica'
        ))

        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#2c5282'),
            spaceBefore=20,
            spaceAfter=12,
            fontName='Helvetica-Bold'
        ))

        self.styles.add(ParagraphStyle(
            name='SubsectionHeader',
            parent=self.styles['Heading3'],
            fontSize=13,
            textColor=colors.HexColor('#2d3748'),
            spaceBefore=15,
            spaceAfter=8,
            fontName='Helvetica-Bold'
        ))

        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#2d3748'),
            spaceAfter=10,
            alignment=TA_JUSTIFY,
            leading=14
        ))

        self.styles.add(ParagraphStyle(
            name='CustomBullet',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#2d3748'),
            spaceAfter=6,
            leftIndent=20,
            bulletIndent=10,
            leading=14
        ))

        self.styles.add(ParagraphStyle(
            name='Recommendation',
            parent=self.styles['Normal'],
            fontSize=14,
            textColor=colors.white,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold',
            leading=18
        ))

        self.styles.add(ParagraphStyle(
            name='Disclaimer',
            parent=self.styles['Normal'],
            fontSize=8,
            textColor=colors.HexColor('#718096'),
            spaceAfter=6,
            alignment=TA_JUSTIFY,
            leading=10
        ))

    def _add_header(self):
        title = Paragraph(
            f"<b>Investment Analysis Report</b><br/>{self.ticker}",
            self.styles['CustomTitle']
        )
        self.elements.append(title)

        subtitle_text = ""
        if self.company_name:
            subtitle_text += f"{self.company_name}<br/>"
        subtitle_text += f"<i>Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</i>"
        subtitle = Paragraph(subtitle_text, self.styles['CustomSubtitle'])
        self.elements.append(subtitle)

        self.elements.append(Spacer(1, 0.2 * inch))
        self._add_separator_line()
        self.elements.append(Spacer(1, 0.3 * inch))

    def _add_separator_line(self):
        line_table = Table([[""]], colWidths=[6.5 * inch])
        line_table.setStyle(TableStyle([
            ('LINEABOVE', (0, 0), (-1, 0), 2, colors.HexColor('#2c5282')),
        ]))
        self.elements.append(line_table)

    def _create_recommendation_box(self, recommendation):
        rec_lower = recommendation.lower()
        if 'strong buy' in rec_lower:
            bg_color = colors.HexColor('#22543d')
        elif 'buy' in rec_lower:
            bg_color = colors.HexColor('#2f855a')
        elif 'hold' in rec_lower:
            bg_color = colors.HexColor('#d69e2e')
        elif 'sell' in rec_lower:
            bg_color = colors.HexColor('#c53030')
        else:
            bg_color = colors.HexColor('#4a5568')

        data = [[Paragraph("<b>INVESTMENT RECOMMENDATION</b>", self.styles['Recommendation'])],
                [Paragraph(f"<b>{recommendation.upper()}</b>", self.styles['Recommendation'])]]

        table = Table(data, colWidths=[6.5 * inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), bg_color),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('PADDING', (0, 0), (-1, -1), 15),
            ('TOPPADDING', (0, 1), (-1, 1), 20),
            ('BOTTOMPADDING', (0, 1), (-1, 1), 20),
            ('BOX', (0, 0), (-1, -1), 2, colors.white),
        ]))

        return table

    def _parse_markdown_content(self):
        lines = self.content.split('\n')
        current_section = []
        recommendation = None

        for line in lines:
            lower_line = line.lower()
            if any(skip in lower_line for skip in ['delegate', 'coordination', 'okay, i will']):
                continue
            if line.strip().startswith('```'):
                continue

            if line.startswith('# ') and 'Team Investment' not in line:
                if current_section:
                    self._add_section_content(current_section)
                    current_section = []
                title = line.replace('#', '').strip()
                self.elements.append(Spacer(1, 0.2 * inch))
                self.elements.append(Paragraph(title, self.styles['SectionHeader']))
                self.elements.append(Spacer(1, 0.1 * inch))

            elif line.startswith('## '):
                if current_section:
                    self._add_section_content(current_section)
                    current_section = []
                title = line.replace('##', '').strip()
                self.elements.append(Spacer(1, 0.15 * inch))
                self.elements.append(Paragraph(title, self.styles['SubsectionHeader']))

            elif line.startswith('### '):
                title = line.replace('###', '').strip()
                self.elements.append(Paragraph(f"<b>{title}</b>", self.styles['CustomBody']))

            elif line.strip().startswith(('*', '-')):
                text = line.strip()[1:].strip()
                if text:
                    bullet_text = f"• {text}"
                    self.elements.append(Paragraph(bullet_text, self.styles['CustomBullet']))

            elif line.strip():
                if 'recommendation:' in lower_line or 'recommendation**' in lower_line:
                    recommendation = self._extract_recommendation(lower_line)
                current_section.append(line.strip())

        if current_section:
            self._add_section_content(current_section)

        if recommendation:
            self.elements.append(Spacer(1, 0.3 * inch))
            self.elements.append(self._create_recommendation_box(recommendation))
            self.elements.append(Spacer(1, 0.2 * inch))

    def _extract_recommendation(self, line):
        rec_patterns = ['strong buy', 'buy', 'hold', 'sell', 'strong sell']
        for pattern in rec_patterns:
            if pattern in line:
                return pattern.title()
        return "Hold"

    def _add_section_content(self, content_lines):
        text = ' '.join(content_lines)
        if text:
            text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
            text = re.sub(r'\*(.*?)\*', r'<i>\1</i>', text)
            text = re.sub(r'`(.*?)`', r'<i>\1</i>', text)
            para = Paragraph(text, self.styles['CustomBody'])
            self.elements.append(para)
            self.elements.append(Spacer(1, 0.1 * inch))

    def _add_footer(self):
        self.elements.append(Spacer(1, 0.3 * inch))
        self._add_separator_line()
        self.elements.append(Spacer(1, 0.2 * inch))

        disclaimer = (
            "<b>DISCLAIMER:</b> This investment report is for informational purposes only and should not be "
            "considered financial advice. The information contained herein is based on current market conditions "
            "and analysis, which are subject to change. Investors should conduct their own due diligence and "
            "consult with a qualified financial advisor before making any investment decisions. Past performance "
            "is not indicative of future results. Investing in securities involves risk, including the potential "
            "loss of principal."
        )
        self.elements.append(Paragraph(disclaimer, self.styles['Disclaimer']))

        footer_text = (
            f"<i>Report generated by AI Investment Analysis System | {datetime.now().strftime('%B %d, %Y')}</i>"
        )
        self.elements.append(Spacer(1, 0.1 * inch))
        self.elements.append(Paragraph(footer_text, self.styles['Disclaimer']))

    def _add_page_number(self, canvas, doc):
        page_num = canvas.getPageNumber()
        canvas.setFont('Helvetica', 8)
        canvas.setFillColor(colors.HexColor('#718096'))
        canvas.drawRightString(7.5 * inch, 0.5 * inch, f"Page {page_num}")
        canvas.drawString(1 * inch, 0.5 * inch, f"{self.ticker} Investment Report")

    def generate(self):
        self._add_header()
        self._parse_markdown_content()
        self._add_footer()

        self.doc.build(
            self.elements,
            onFirstPage=self._add_page_number,
            onLaterPages=self._add_page_number
        )
        return self.filename


def generate_pdf_report(ticker, company_name, content, output_dir="reports/output"):
    pdf = InvestmentReportPDF(ticker, company_name, content, output_dir)
    return pdf.generate()


if __name__ == "__main__":
    sample_content = """
    # Investment Analysis Report

    ## Executive Summary

    This is a test report with **bold text** and *italic text*.

    ## Financial Analysis

    * Revenue: $100B
    * Profit Margin: 25%
    * P/E Ratio: 30

    ## Recommendation

    **Recommendation:** Buy

    Based on our analysis, we recommend a **Buy** rating for this stock.
    """

    pdf_file = generate_pdf_report("TEST", "Test Company", sample_content)
    print(f"Test PDF generated: {pdf_file}")
