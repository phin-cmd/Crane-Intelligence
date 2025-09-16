"""
Simple PDF Export Service
Handles PDF generation using browser-based approach without external dependencies
"""

import os
import logging
from typing import Dict, Any, Optional
from pathlib import Path
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class SimplePDFExportService:
    """Handles PDF export using browser-based generation"""
    
    def __init__(self):
        self.output_dir = Path("backend/generated_reports")
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_html_report(self, report_data: Dict[str, Any], report_id: str) -> str:
        """
        Generate HTML report that can be printed to PDF by the browser
        
        Args:
            report_data: Report data dictionary
            report_id: Unique report identifier
            
        Returns:
            Path to generated HTML file
        """
        try:
            logger.info(f"Generating HTML report for {report_id}")
            
            # Generate HTML filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            html_filename = f"{report_id}_{timestamp}.html"
            html_path = self.output_dir / html_filename
            
            # Create HTML content
            html_content = self._create_html_report(report_data, report_id)
            
            # Write HTML file
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.info(f"HTML report generated: {html_path}")
            return str(html_path)
            
        except Exception as e:
            logger.error(f"Error generating HTML report: {e}")
            raise Exception(f"HTML report generation failed: {str(e)}")
    
    def generate_dual_reports(self, report_data: Dict[str, Any], report_id: str) -> Dict[str, str]:
        """
        Generate both Market Intelligence Report and Cover Letter
        
        Args:
            report_data: Report data dictionary
            report_id: Unique report identifier
            
        Returns:
            Dictionary with paths to both generated HTML files
        """
        try:
            logger.info(f"Generating dual reports for {report_id}")
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Generate Market Intelligence Report
            market_intel_filename = f"{report_id}_market_intelligence_{timestamp}.html"
            market_intel_path = self.output_dir / market_intel_filename
            market_intel_content = self._create_market_intelligence_report(report_data, report_id)
            
            with open(market_intel_path, 'w', encoding='utf-8') as f:
                f.write(market_intel_content)
            
            # Generate Cover Letter
            cover_letter_filename = f"{report_id}_cover_letter_{timestamp}.html"
            cover_letter_path = self.output_dir / cover_letter_filename
            cover_letter_content = self._create_cover_letter_report(report_data, report_id)
            
            with open(cover_letter_path, 'w', encoding='utf-8') as f:
                f.write(cover_letter_content)
            
            logger.info(f"Dual reports generated: {market_intel_path}, {cover_letter_path}")
            return {
                'market_intelligence': str(market_intel_path),
                'cover_letter': str(cover_letter_path)
            }
            
        except Exception as e:
            logger.error(f"Error generating dual reports: {e}")
            raise Exception(f"Dual report generation failed: {str(e)}")
    
    def _create_html_report(self, report_data: Dict[str, Any], report_id: str) -> str:
        """Create HTML content for the report"""
        
        valuation_data = report_data.get('valuation_data', {})
        kpi_metrics = report_data.get('kpi_metrics', {})
        comparable_sales = report_data.get('comparable_sales', [])
        finance_scenarios = report_data.get('finance_scenarios', [])
        market_analysis = report_data.get('market_analysis', {})
        risk_assessment = report_data.get('risk_assessment', {})
        
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Crane Intelligence Report - {report_id}</title>
    <style>
        {self._get_pdf_css()}
    </style>
</head>
<body>
    <div class="report-container">
        <!-- Header -->
        <div class="report-header">
            <h1 class="report-title">Crane Intelligence Report</h1>
            <p class="report-subtitle">Professional Equipment Valuation & Market Analysis</p>
            <div class="report-meta">
                <span>Report ID: {report_id}</span>
                <span>Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</span>
            </div>
        </div>
        
        <!-- KPI Metrics -->
        <div class="section">
            <h2 class="section-title">Key Performance Indicators</h2>
            <div class="kpi-grid">
                <div class="kpi-card">
                    <div class="kpi-value">${kpi_metrics.get('estimated_value', 0):,.0f}</div>
                    <div class="kpi-label">Estimated Value</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-value">${kpi_metrics.get('value_per_ton', 0):,.0f}</div>
                    <div class="kpi-label">Value per Ton</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-value">{kpi_metrics.get('confidence_score', 0)}%</div>
                    <div class="kpi-label">Confidence Score</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-value">{kpi_metrics.get('age_factor', 0)*100:.0f}%</div>
                    <div class="kpi-label">Age Factor</div>
                </div>
            </div>
        </div>
        
        <!-- Equipment Details -->
        <div class="section">
            <h2 class="section-title">Equipment Details</h2>
            <div class="details-grid">
                <div class="detail-item">
                    <span class="detail-label">Manufacturer:</span>
                    <span class="detail-value">{valuation_data.get('manufacturer', 'N/A')}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Model:</span>
                    <span class="detail-value">{valuation_data.get('model', 'N/A')}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Year:</span>
                    <span class="detail-value">{valuation_data.get('year', 'N/A')}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Capacity:</span>
                    <span class="detail-value">{valuation_data.get('capacity_tons', 0):.0f} Tons</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Hours:</span>
                    <span class="detail-value">{valuation_data.get('hours', 0):,}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Region:</span>
                    <span class="detail-value">{valuation_data.get('region', 'N/A')}</span>
                </div>
            </div>
        </div>
        
        <!-- Comparable Sales -->
        <div class="section">
            <h2 class="section-title">Comparable Sales</h2>
            <table class="table">
                <thead>
                    <tr>
                        <th>Manufacturer</th>
                        <th>Model</th>
                        <th>Year</th>
                        <th>Price</th>
                        <th>Location</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        for sale in comparable_sales:
            html += f"""
                    <tr>
                        <td>{sale.get('manufacturer', 'N/A')}</td>
                        <td>{sale.get('model', 'N/A')}</td>
                        <td>{sale.get('year', 'N/A')}</td>
                        <td>${sale.get('price', 0):,.0f}</td>
                        <td>{sale.get('location', 'N/A')}</td>
                    </tr>
            """
        
        html += """
                </tbody>
            </table>
        </div>
        
        <!-- Finance Scenarios -->
        <div class="section">
            <h2 class="section-title">Finance Scenarios</h2>
            <div class="scenario-grid">
        """
        
        for scenario in finance_scenarios:
            html += f"""
                <div class="scenario-card">
                    <div class="scenario-title">{scenario.get('scenario', 'N/A')}</div>
                    <div class="scenario-value">${scenario.get('monthly_payment', 0):,.0f}</div>
                    <div class="scenario-label">Monthly Payment</div>
                    <div class="scenario-detail">5-Year Total: ${scenario.get('total_cost_5yr', 0):,.0f}</div>
                    <div class="scenario-detail">ROI: {scenario.get('roi', 0)}%</div>
                </div>
            """
        
        html += f"""
            </div>
        </div>
        
        <!-- Market Analysis -->
        <div class="section">
            <h2 class="section-title">Market Analysis</h2>
            <div class="analysis-grid">
                <div class="analysis-item">
                    <span class="analysis-label">Demand Level:</span>
                    <span class="analysis-value">{market_analysis.get('demand_level', 'N/A')}</span>
                </div>
                <div class="analysis-item">
                    <span class="analysis-label">Market Trend:</span>
                    <span class="analysis-value">{market_analysis.get('market_trend', 'N/A')}</span>
                </div>
                <div class="analysis-item">
                    <span class="analysis-label">Price Trend:</span>
                    <span class="analysis-value">{market_analysis.get('price_trend', 'N/A')}</span>
                </div>
                <div class="analysis-item">
                    <span class="analysis-label">Regional Factors:</span>
                    <span class="analysis-value">{market_analysis.get('regional_factors', 'N/A')}</span>
                </div>
            </div>
        </div>
        
        <!-- Risk Assessment -->
        <div class="section">
            <h2 class="section-title">Risk Assessment</h2>
            <div class="risk-grid">
                <div class="risk-item">
                    <span class="risk-label">Overall Risk:</span>
                    <span class="risk-value risk-{risk_assessment.get('overall_risk', 'medium').lower()}">{risk_assessment.get('overall_risk', 'N/A')}</span>
                </div>
                <div class="risk-item">
                    <span class="risk-label">Market Risk:</span>
                    <span class="risk-value risk-{risk_assessment.get('market_risk', 'medium').lower()}">{risk_assessment.get('market_risk', 'N/A')}</span>
                </div>
                <div class="risk-item">
                    <span class="risk-label">Operational Risk:</span>
                    <span class="risk-value risk-{risk_assessment.get('operational_risk', 'medium').lower()}">{risk_assessment.get('operational_risk', 'N/A')}</span>
                </div>
                <div class="risk-item">
                    <span class="risk-label">Financial Risk:</span>
                    <span class="risk-value risk-{risk_assessment.get('financial_risk', 'medium').lower()}">{risk_assessment.get('financial_risk', 'N/A')}</span>
                </div>
            </div>
        </div>
        
        <!-- Footer -->
        <div class="footer">
            <p>Generated by Crane Intelligence Platform | Report ID: {report_id} | {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
            <p>This report is for informational purposes only and should not be considered as financial advice.</p>
        </div>
    </div>
    
    <script>
        // Add print functionality
        function printReport() {{
            window.print();
        }}
        
        // Auto-print when loaded (optional)
        // window.onload = function() {{ printReport(); }};
    </script>
</body>
</html>
        """
        
        return html
    
    def _get_pdf_css(self) -> str:
        """Get CSS styles optimized for PDF generation"""
        return """
        @page {
            size: A4 landscape;
            margin: 0.75in;
        }
        
        * {
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Inter', 'Arial', sans-serif;
            font-size: 12px;
            line-height: 1.4;
            color: #000000;
            background: #ffffff;
            margin: 0;
            padding: 0;
        }
        
        .report-container {
            max-width: 100%;
            margin: 0 auto;
            padding: 20px;
        }
        
        .report-header {
            background: linear-gradient(135deg, #00FF85, #00CC6A);
            color: #000000;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 30px;
            text-align: center;
        }
        
        .report-title {
            font-size: 24px;
            font-weight: 800;
            margin: 0 0 10px 0;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .report-subtitle {
            font-size: 14px;
            margin: 0 0 15px 0;
            opacity: 0.8;
        }
        
        .report-meta {
            font-size: 11px;
            opacity: 0.7;
        }
        
        .report-meta span {
            margin-right: 20px;
        }
        
        .kpi-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 15px;
            margin-bottom: 30px;
        }
        
        .kpi-card {
            background: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 6px;
            padding: 15px;
            text-align: center;
        }
        
        .kpi-value {
            font-size: 18px;
            font-weight: 700;
            color: #00FF85;
            margin-bottom: 5px;
        }
        
        .kpi-label {
            font-size: 11px;
            color: #666666;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .section {
            margin-bottom: 30px;
            page-break-inside: avoid;
        }
        
        .section-title {
            font-size: 16px;
            font-weight: 600;
            color: #333333;
            margin-bottom: 15px;
            padding-bottom: 5px;
            border-bottom: 2px solid #00FF85;
        }
        
        .details-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 15px;
            margin-bottom: 20px;
        }
        
        .detail-item {
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px solid #e9ecef;
        }
        
        .detail-label {
            font-weight: 600;
            color: #666666;
        }
        
        .detail-value {
            color: #000000;
        }
        
        .table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
        }
        
        .table th,
        .table td {
            padding: 8px 12px;
            text-align: left;
            border: 1px solid #e9ecef;
        }
        
        .table th {
            background: #f8f9fa;
            font-weight: 600;
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .table td {
            font-size: 11px;
        }
        
        .scenario-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 15px;
            margin-bottom: 20px;
        }
        
        .scenario-card {
            background: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 6px;
            padding: 15px;
        }
        
        .scenario-title {
            font-size: 12px;
            font-weight: 600;
            color: #333333;
            margin-bottom: 10px;
        }
        
        .scenario-value {
            font-size: 14px;
            font-weight: 700;
            color: #00FF85;
            margin-bottom: 5px;
        }
        
        .scenario-label {
            font-size: 10px;
            color: #666666;
            margin-bottom: 3px;
        }
        
        .scenario-detail {
            font-size: 9px;
            color: #888888;
        }
        
        .analysis-grid,
        .risk-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 15px;
            margin-bottom: 20px;
        }
        
        .analysis-item,
        .risk-item {
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px solid #e9ecef;
        }
        
        .analysis-label,
        .risk-label {
            font-weight: 600;
            color: #666666;
        }
        
        .analysis-value {
            color: #000000;
        }
        
        .risk-value {
            font-weight: 600;
            padding: 2px 8px;
            border-radius: 3px;
        }
        
        .risk-low {
            background: #d4edda;
            color: #155724;
        }
        
        .risk-medium {
            background: #fff3cd;
            color: #856404;
        }
        
        .risk-high {
            background: #f8d7da;
            color: #721c24;
        }
        
        .footer {
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #e9ecef;
            text-align: center;
            font-size: 10px;
            color: #666666;
        }
        
        .footer p {
            margin: 5px 0;
        }
        
        /* Print-specific styles */
        @media print {
            body {
                -webkit-print-color-adjust: exact;
                color-adjust: exact;
            }
            
            .report-header {
                background: #00FF85 !important;
                -webkit-print-color-adjust: exact;
            }
            
            .kpi-value,
            .scenario-value {
                color: #00FF85 !important;
                -webkit-print-color-adjust: exact;
            }
            
            .section {
                page-break-inside: avoid;
            }
        }
        """
    
    def _create_market_intelligence_report(self, report_data: Dict[str, Any], report_id: str) -> str:
        """Create Market Intelligence Report HTML content"""
        
        valuation_data = report_data.get('valuation_data', {})
        
        # Read the template file
        template_path = Path("backend/templates/reports/market_intelligence.html")
        if template_path.exists():
            with open(template_path, 'r', encoding='utf-8') as f:
                template_content = f.read()
        else:
            # Fallback template if file doesn't exist
            template_content = self._get_market_intelligence_template()
        
        # Replace placeholders
        html_content = template_content.format(
            report_metadata={
                'report_id': report_id,
                'generated_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            },
            valuation_data=valuation_data
        )
        
        return html_content
    
    def _create_cover_letter_report(self, report_data: Dict[str, Any], report_id: str) -> str:
        """Create Cover Letter HTML content"""
        
        valuation_data = report_data.get('valuation_data', {})
        
        # Read the template file
        template_path = Path("backend/templates/reports/cover_letter.html")
        if template_path.exists():
            with open(template_path, 'r', encoding='utf-8') as f:
                template_content = f.read()
        else:
            # Fallback template if file doesn't exist
            template_content = self._get_cover_letter_template()
        
        # Replace placeholders
        html_content = template_content.format(
            report_metadata={
                'report_id': report_id,
                'generated_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            },
            valuation_data=valuation_data
        )
        
        return html_content
    
    def _get_market_intelligence_template(self) -> str:
        """Fallback Market Intelligence template if file not found"""
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Market Intelligence Report - {report_metadata[report_id]}</title>
</head>
<body>
    <h1>Market Intelligence Report</h1>
    <p>Report ID: {report_metadata[report_id]}</p>
    <p>Generated: {report_metadata[generated_at]}</p>
    <p>Equipment: {valuation_data[manufacturer]} {valuation_data[model]} ({valuation_data[year]})</p>
    <p>Estimated Value: ${valuation_data[estimated_value]:,.0f}</p>
</body>
</html>
"""
    
    def _get_cover_letter_template(self) -> str:
        """Fallback Cover Letter template if file not found"""
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Cover Letter - {report_metadata[report_id]}</title>
</head>
<body>
    <h1>Crane Intelligence Cover Letter</h1>
    <p>Report ID: {report_metadata[report_id]}</p>
    <p>Generated: {report_metadata[generated_at]}</p>
    <p>Equipment: {valuation_data[manufacturer]} {valuation_data[model]} ({valuation_data[year]})</p>
    <p>Estimated Value: ${valuation_data[estimated_value]:,.0f}</p>
</body>
</html>
"""
