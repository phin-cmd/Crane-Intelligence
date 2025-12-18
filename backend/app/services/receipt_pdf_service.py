"""
PDF Receipt Generation Service
Generates professional PDF receipts for FMV report payments
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime
from io import BytesIO
from pathlib import Path

try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib import colors
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    logging.warning("reportlab not available - PDF receipt generation will be disabled")

from ..core.config import settings

logger = logging.getLogger(__name__)


class ReceiptPDFService:
    """Service for generating PDF receipts"""
    
    def __init__(self):
        if not REPORTLAB_AVAILABLE:
            logger.warning("reportlab library not available. Install with: pip install reportlab")
            self.available = False
        else:
            self.available = True
    
    def generate_receipt_pdf(self, receipt_data: Dict[str, Any]) -> Optional[BytesIO]:
        """
        Generate a PDF receipt for payment
        
        Args:
            receipt_data: Dictionary containing:
                - receipt_number: Receipt number/ID
                - transaction_id: Payment intent ID or transaction ID
                - payment_date: Payment date
                - customer_name: Customer full name
                - customer_email: Customer email
                - report_id: FMV Report ID
                - report_type: Type of report (spot_check, professional, fleet_valuation)
                - amount: Payment amount
                - currency: Currency code (default: USD)
                - company_name: Company name (optional)
                - address: Customer address (optional)
        
        Returns:
            BytesIO object containing PDF data, or None if generation fails
        """
        if not self.available:
            logger.error("PDF generation not available - reportlab library missing")
            return None
        
        try:
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
            story = []
            styles = getSampleStyleSheet()
            
            # Custom styles
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#1a1a1a'),
                spaceAfter=30,
                alignment=TA_CENTER
            )
            
            heading_style = ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading2'],
                fontSize=14,
                textColor=colors.HexColor('#333333'),
                spaceAfter=12,
                spaceBefore=12
            )
            
            normal_style = ParagraphStyle(
                'CustomNormal',
                parent=styles['Normal'],
                fontSize=10,
                textColor=colors.HexColor('#666666'),
                spaceAfter=6
            )
            
            # Company header
            company_name = receipt_data.get('company_name', settings.app_name)
            story.append(Paragraph(company_name, title_style))
            story.append(Spacer(1, 0.2*inch))
            
            # Receipt title
            story.append(Paragraph("PAYMENT RECEIPT", heading_style))
            story.append(Spacer(1, 0.1*inch))
            
            # Receipt details table
            receipt_number = receipt_data.get('receipt_number', receipt_data.get('transaction_id', 'N/A'))
            transaction_id = receipt_data.get('transaction_id', receipt_data.get('payment_intent_id', 'N/A'))
            payment_date = receipt_data.get('payment_date', datetime.now().strftime('%B %d, %Y at %I:%M %p'))
            if isinstance(payment_date, str):
                try:
                    # Try to parse and format if it's an ISO string
                    dt = datetime.fromisoformat(payment_date.replace('Z', '+00:00'))
                    payment_date = dt.strftime('%B %d, %Y at %I:%M %p')
                except:
                    pass
            
            # Customer information
            customer_name = receipt_data.get('customer_name', 'Customer')
            customer_email = receipt_data.get('customer_email', '')
            address = receipt_data.get('address', '')
            
            # Report information
            report_id = receipt_data.get('report_id', 'N/A')
            report_type = receipt_data.get('report_type', 'N/A')
            report_type_display = report_type.replace('_', ' ').title() if report_type else 'FMV Report'
            
            # Payment information
            amount = receipt_data.get('amount', 0)
            currency = receipt_data.get('currency', 'USD')
            amount_display = f"${amount:,.2f}" if currency == 'USD' else f"{currency} {amount:,.2f}"
            
            # Create receipt details table
            receipt_details = [
                ['Receipt Number:', receipt_number],
                ['Transaction ID:', transaction_id],
                ['Payment Date:', payment_date],
                ['', ''],  # Spacer row
                ['Customer Name:', customer_name],
                ['Email:', customer_email],
            ]
            
            if address:
                receipt_details.append(['Address:', address])
            
            receipt_details.extend([
                ['', ''],  # Spacer row
                ['Report ID:', f"#{report_id}"],
                ['Report Type:', report_type_display],
                ['', ''],  # Spacer row
                ['Amount Paid:', f"<b>{amount_display}</b>"],
            ])
            
            # Create table
            receipt_table = Table(receipt_details, colWidths=[2*inch, 4*inch])
            receipt_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f5f5f5')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]))
            
            story.append(receipt_table)
            story.append(Spacer(1, 0.3*inch))
            
            # Footer
            footer_text = f"""
            <para align="center">
            <b>Thank you for your payment!</b><br/>
            This is an official receipt for your transaction.<br/>
            For questions or support, please contact: {settings.mail_from_email}<br/>
            <br/>
            {company_name}<br/>
            {settings.frontend_url}
            </para>
            """
            story.append(Paragraph(footer_text, normal_style))
            
            # Build PDF
            doc.build(story)
            buffer.seek(0)
            
            logger.info(f"✅ Generated PDF receipt for transaction {transaction_id}")
            return buffer
            
        except Exception as e:
            logger.error(f"❌ Error generating PDF receipt: {e}", exc_info=True)
            return None
    
    def generate_receipt_pdf_base64(self, receipt_data: Dict[str, Any]) -> Optional[str]:
        """
        Generate PDF receipt and return as base64 string for email attachment
        
        Args:
            receipt_data: Same as generate_receipt_pdf
        
        Returns:
            Base64 encoded string of PDF, or None if generation fails
        """
        pdf_buffer = self.generate_receipt_pdf(receipt_data)
        if pdf_buffer:
            import base64
            return base64.b64encode(pdf_buffer.getvalue()).decode('utf-8')
        return None

