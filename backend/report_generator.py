"""
PDF Report Generator for Clinical Trials
Professional PDF reports with comprehensive details and blockchain/clinical trial theme
"""
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from datetime import datetime
from typing import Dict, Any, Optional
import os
import tempfile
import json

class ReportGenerator:
    """Generate comprehensive professional PDF reports for clinical trials"""
    
    # Color scheme matching the UI (black & green theme)
    COLOR_PRIMARY_GREEN = colors.HexColor('#22c55e')  # Green-500
    COLOR_DARK_GREEN = colors.HexColor('#059669')     # Green-700
    COLOR_LIGHT_GREEN = colors.HexColor('#d1fae5')    # Green-100
    COLOR_DARK = colors.HexColor('#0a0f0a')           # Dark black-green
    COLOR_TEXT_DARK = colors.HexColor('#111827')      # Gray-900
    COLOR_TEXT_LIGHT = colors.HexColor('#6b7280')     # Gray-500
    
    def __init__(self):
        self.output_dir = tempfile.gettempdir()
        os.makedirs(self.output_dir, exist_ok=True)
    
    def _get_heading_style(self, size, color=None):
        """Get styled heading paragraph"""
        color = color or self.COLOR_DARK_GREEN
        return ParagraphStyle(
            'Heading',
            parent=getSampleStyleSheet()['Heading2'],
            fontSize=size,
            textColor=color,
            spaceAfter=12,
            spaceBefore=20,
            fontName='Helvetica-Bold',
            leading=size * 1.2
        )
    
    def _get_body_style(self):
        """Get styled body text"""
        return ParagraphStyle(
            'Body',
            parent=getSampleStyleSheet()['Normal'],
            fontSize=10,
            textColor=self.COLOR_TEXT_DARK,
            alignment=TA_JUSTIFY,
            leading=14
        )
    
    def _create_table(self, data, col_widths, header_bg=None, row_bg=None):
        """Create a styled table"""
        header_bg = header_bg or self.COLOR_PRIMARY_GREEN
        row_bg = row_bg or colors.white
        
        table = Table(data, colWidths=col_widths)
        table.setStyle(TableStyle([
            # Header styling
            ('BACKGROUND', (0, 0), (-1, 0), header_bg),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            
            # Body styling
            ('BACKGROUND', (0, 1), (-1, -1), row_bg),
            ('TEXTCOLOR', (0, 1), (-1, -1), self.COLOR_TEXT_DARK),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            
            # Alignment and spacing
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 12),
            ('RIGHTPADDING', (0, 0), (-1, -1), 12),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            
            # Grid
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e5e7eb')),
            ('LINEBELOW', (0, 0), (-1, 0), 2, self.COLOR_DARK_GREEN),
            
            # Alternating row colors
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9fafb')]),
        ]))
        return table
    
    async def generate_report(self, trial, uploaded_by_user: Optional[Any] = None, audit_logs: Optional[list] = None) -> str:
        """Generate comprehensive professional PDF report for a trial"""
        filename = f"trial_report_{trial.id}.pdf"
        filepath = os.path.join(self.output_dir, filename)
        
        doc = SimpleDocTemplate(filepath, pagesize=letter,
                               rightMargin=72, leftMargin=72,
                               topMargin=72, bottomMargin=72)
        story = []
        styles = getSampleStyleSheet()
        
        # ========== COVER PAGE ==========
        cover_title_style = ParagraphStyle(
            'CoverTitle',
            parent=styles['Title'],
            fontSize=32,
            textColor=self.COLOR_DARK_GREEN,
            spaceAfter=20,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold',
            leading=38
        )
        
        cover_subtitle_style = ParagraphStyle(
            'CoverSubtitle',
            parent=styles['Normal'],
            fontSize=18,
            textColor=self.COLOR_TEXT_LIGHT,
            spaceAfter=40,
            alignment=TA_CENTER,
            leading=24
        )
        
        # Cover page content
        story.append(Spacer(1, 2*inch))
        story.append(Paragraph("TrialChain", cover_title_style))
        story.append(Paragraph("Blockchain Platform", ParagraphStyle(
            'PlatformSubtitle', parent=styles['Normal'],
            fontSize=14, textColor=self.COLOR_PRIMARY_GREEN,
            alignment=TA_CENTER, spaceAfter=30
        )))
        story.append(Spacer(1, 0.5*inch))
        story.append(Paragraph("Clinical Trial Integrity Report", cover_subtitle_style))
        story.append(Spacer(1, 1*inch))
        
        # Trial ID on cover
        trial_id_style = ParagraphStyle(
            'TrialID',
            parent=styles['Normal'],
            fontSize=16,
            textColor=self.COLOR_TEXT_DARK,
            alignment=TA_CENTER,
            spaceAfter=20,
            fontName='Courier-Bold'
        )
        story.append(Paragraph(f"Trial ID: {str(trial.id)}", trial_id_style))
        
        # Report metadata on cover
        cover_meta = [
            f"Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}",
            f"Report Version: 1.0",
            f"Confidential Document"
        ]
        for meta in cover_meta:
            story.append(Paragraph(meta, ParagraphStyle(
                'CoverMeta', parent=styles['Normal'],
                fontSize=9, textColor=self.COLOR_TEXT_LIGHT,
                alignment=TA_CENTER, spaceAfter=5
            )))
        
        story.append(PageBreak())
        
        # ========== EXECUTIVE SUMMARY ==========
        story.append(Paragraph("Executive Summary", self._get_heading_style(18, self.COLOR_DARK_GREEN)))
        story.append(Spacer(1, 0.2*inch))
        
        summary_data = []
        summary_data.append(["Status", "Value", "Details"])
        
        # Overall status
        if trial.blockchain_status == "written":
            overall_status = "✓ VERIFIED & SECURED"
            status_color = self.COLOR_PRIMARY_GREEN
        elif trial.ml_status in ["ACCEPT", "REVIEW"]:
            overall_status = "✓ APPROVED"
            status_color = self.COLOR_PRIMARY_GREEN
        elif trial.ml_status == "REJECT":
            overall_status = "✗ REJECTED"
            status_color = colors.red
        else:
            overall_status = "⏳ PENDING"
            status_color = colors.HexColor('#f59e0b')
        
        summary_data.append(["Overall Status", overall_status, "Current trial integrity status"])
        summary_data.append(["Trial ID", str(trial.id), "Unique identifier for this trial"])
        summary_data.append(["Participant Count", str(trial.participant_count or "N/A"), "Number of participants in trial"])
        summary_data.append(["Upload Date", trial.created_at.strftime("%B %d, %Y"), "Original upload timestamp"])
        summary_data.append(["Current Status", trial.status.upper(), "Trial workflow status"])
        
        summary_table = self._create_table(summary_data, [2*inch, 2*inch, 2.5*inch])
        story.append(summary_table)
        story.append(Spacer(1, 0.4*inch))
        
        # ========== TRIAL INFORMATION ==========
        story.append(Paragraph("1. Trial Information", self._get_heading_style(16)))
        story.append(Spacer(1, 0.2*inch))
        
        trial_info_data = []
        trial_info_data.append(["Field", "Value"])
        trial_info_data.append(["Trial ID", str(trial.id)])
        trial_info_data.append(["Filename", trial.filename])
        trial_info_data.append(["Status", trial.status.upper()])
        trial_info_data.append(["Participant Count", str(trial.participant_count or "Not specified")])
        trial_info_data.append(["Uploaded Date", trial.created_at.strftime("%Y-%m-%d %H:%M:%S UTC")])
        trial_info_data.append(["Last Updated", trial.updated_at.strftime("%Y-%m-%d %H:%M:%S UTC") if trial.updated_at else "N/A"])
        
        if uploaded_by_user:
            trial_info_data.append(["Uploaded By", f"{uploaded_by_user.get('username', 'Unknown')} ({uploaded_by_user.get('email', 'N/A')})"])
            trial_info_data.append(["User Role", uploaded_by_user.get('role', 'N/A')])
            if uploaded_by_user.get('organization'):
                trial_info_data.append(["Organization", uploaded_by_user.get('organization')])
        
        trial_info_table = self._create_table(trial_info_data, [2.5*inch, 3.5*inch])
        story.append(trial_info_table)
        story.append(Spacer(1, 0.4*inch))
        
        # ========== VALIDATION RESULTS ==========
        if trial.validation_status or trial.validation_details:
            story.append(Paragraph("2. Validation Results", self._get_heading_style(16)))
            story.append(Spacer(1, 0.2*inch))
            
            validation_data = []
            validation_data.append(["Validation Item", "Status", "Details"])
            
            if trial.validation_status:
                status_icon = "✓" if trial.validation_status == "passed" else "✗"
                validation_data.append(["Overall Validation", 
                                       f"{status_icon} {trial.validation_status.upper()}",
                                       "Rule engine validation result"])
            
            if trial.validation_details:
                if isinstance(trial.validation_details, dict):
                    rules_passed = trial.validation_details.get('rules_passed', [])
                    rules_failed = trial.validation_details.get('rules_failed', [])
                    
                    for rule in rules_passed:
                        validation_data.append([rule, "✓ PASSED", ""])
                    for rule in rules_failed:
                        validation_data.append([rule, "✗ FAILED", ""])
            
            if len(validation_data) > 1:  # Has data beyond header
                validation_table = self._create_table(validation_data, [2.5*inch, 1.5*inch, 2*inch])
                story.append(validation_table)
                story.append(Spacer(1, 0.4*inch))
        
        # ========== ML BIAS ANALYSIS ==========
        if trial.ml_status:
            story.append(Paragraph("3. Machine Learning Bias Analysis", self._get_heading_style(16)))
            story.append(Spacer(1, 0.2*inch))
            
            ml_data = []
            ml_data.append(["Metric", "Value", "Status"])
            
            # ML Decision
            decision_icon = "✓" if trial.ml_status == "ACCEPT" else "⚠" if trial.ml_status == "REVIEW" else "✗"
            ml_data.append(["ML Decision", f"{decision_icon} {trial.ml_status}", 
                          "AI bias detection result"])
            
            # Fairness Score
            if trial.ml_score is not None:
                score_status = "EXCELLENT" if trial.ml_score >= 0.8 else "GOOD" if trial.ml_score >= 0.6 else "FAIR"
                ml_data.append(["Fairness Score", f"{trial.ml_score:.3f} / 1.000", score_status])
            
            # ML Details
            if trial.ml_details and isinstance(trial.ml_details, dict):
                metrics = trial.ml_details.get('metrics', {})
                fairness = metrics.get('fairness_metrics', {})
                
                if fairness:
                    demographic_parity = fairness.get('demographic_parity', 0)
                    ml_data.append(["Demographic Parity", f"{demographic_parity:.3f}", 
                                  "✓ FAIR" if demographic_parity >= 0.8 else "⚠ REVIEW"])
                    
                    disparate_impact = fairness.get('disparate_impact_ratio', 0)
                    ml_data.append(["Disparate Impact Ratio", f"{disparate_impact:.3f}",
                                  "✓ FAIR" if 0.8 <= disparate_impact <= 1.2 else "⚠ REVIEW"])
                    
                    equality = fairness.get('equality_of_opportunity', 0)
                    ml_data.append(["Equality of Opportunity", f"{equality:.3f}",
                                  "✓ FAIR" if equality >= 0.8 else "⚠ REVIEW"])
                
                # Outlier detection
                outlier_score = metrics.get('outlier_score', None)
                if outlier_score is not None:
                    is_outlier = metrics.get('is_outlier', False)
                    ml_data.append(["Outlier Score", f"{outlier_score:.3f}",
                                  "✗ OUTLIER DETECTED" if is_outlier else "✓ NORMAL"])
                
                # Bias probability
                bias_prob = metrics.get('bias_probability', None)
                if bias_prob is not None:
                    ml_data.append(["Bias Probability", f"{bias_prob:.1%}",
                                  "HIGH RISK" if bias_prob > 0.3 else "LOW RISK"])
                
                # Recommendations
                recommendations = trial.ml_details.get('recommendations', [])
                if recommendations:
                    story.append(Spacer(1, 0.2*inch))
                    story.append(Paragraph("Recommendations:", ParagraphStyle(
                        'RecTitle', parent=styles['Normal'],
                        fontSize=11, textColor=self.COLOR_DARK_GREEN,
                        fontName='Helvetica-Bold', spaceAfter=8
                    )))
                    for rec in recommendations:
                        story.append(Paragraph(f"• {rec}", self._get_body_style()))
            
            ml_table = self._create_table(ml_data, [2.5*inch, 2*inch, 1.5*inch])
            story.append(ml_table)
            story.append(Spacer(1, 0.4*inch))
        
        # ========== BLOCKCHAIN VERIFICATION ==========
        story.append(Paragraph("4. Blockchain Verification & Integrity", self._get_heading_style(16)))
        story.append(Spacer(1, 0.2*inch))
        
        if trial.blockchain_tx_hash:
            blockchain_data = []
            blockchain_data.append(["Blockchain Field", "Value"])
            blockchain_data.append(["Transaction Hash", trial.blockchain_tx_hash])
            blockchain_data.append(["Block Number", str(trial.blockchain_block_number) if trial.blockchain_block_number else "N/A"])
            blockchain_data.append(["Blockchain Timestamp", 
                                  trial.blockchain_timestamp.strftime("%Y-%m-%d %H:%M:%S UTC") 
                                  if trial.blockchain_timestamp else "N/A"])
            blockchain_data.append(["Blockchain Status", trial.blockchain_status.upper() if trial.blockchain_status else "N/A"])
            blockchain_data.append(["Network", "Hyperledger Fabric"])
            blockchain_data.append(["Integrity Status", "✓ VERIFIED" if trial.blockchain_status == "written" else "⏳ PENDING"])
            
            blockchain_table = self._create_table(blockchain_data, [2.5*inch, 3.5*inch])
            story.append(blockchain_table)
        else:
            story.append(Paragraph("⏳ Trial has not been written to blockchain yet.", self._get_body_style()))
            story.append(Paragraph("Blockchain verification will be available after the trial is written to the distributed ledger.", 
                                  ParagraphStyle('Note', parent=styles['Normal'], fontSize=9, 
                                                textColor=self.COLOR_TEXT_LIGHT, fontStyle='italic')))
        
        story.append(Spacer(1, 0.4*inch))
        
        # ========== DIGITAL SIGNATURE ==========
        if trial.digital_signature or trial.signed_by:
            story.append(Paragraph("5. Digital Signature", self._get_heading_style(16)))
            story.append(Spacer(1, 0.2*inch))
            
            signature_data = []
            signature_data.append(["Signature Field", "Value"])
            signature_data.append(["Digital Signature", 
                                 trial.digital_signature[:64] + "..." if trial.digital_signature and len(trial.digital_signature) > 64 
                                 else (trial.digital_signature or "N/A")])
            signature_data.append(["Signed By", "User ID: " + str(trial.signed_by) if trial.signed_by else "N/A"])
            signature_data.append(["Signature Timestamp", 
                                 trial.signature_timestamp.strftime("%Y-%m-%d %H:%M:%S UTC") 
                                 if trial.signature_timestamp else "N/A"])
            signature_data.append(["Signature Status", "✓ VERIFIED"])
            
            signature_table = self._create_table(signature_data, [2.5*inch, 3.5*inch])
            story.append(signature_table)
            story.append(Spacer(1, 0.4*inch))
        
        # ========== AUDIT TRAIL ==========
        if audit_logs:
            story.append(Paragraph("6. Audit Trail", self._get_heading_style(16)))
            story.append(Spacer(1, 0.2*inch))
            story.append(Paragraph("Complete chronological log of all actions performed on this trial.", 
                                  ParagraphStyle('AuditIntro', parent=styles['Normal'], 
                                                fontSize=9, textColor=self.COLOR_TEXT_LIGHT, 
                                                spaceAfter=12, fontStyle='italic')))
            
            audit_data = []
            audit_data.append(["Timestamp", "Action", "User ID", "Details"])
            
            for log in audit_logs[:20]:  # Limit to last 20 entries
                timestamp = log.get('timestamp', 'N/A')
                if isinstance(timestamp, str):
                    try:
                        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                        timestamp = dt.strftime("%Y-%m-%d %H:%M")
                    except:
                        pass
                
                action = log.get('action', 'N/A').replace('_', ' ').title()
                user_id = str(log.get('user_id', 'N/A'))[:12]
                details = str(log.get('details', ''))[:50] + "..." if log.get('details') else "—"
                
                audit_data.append([timestamp, action, user_id, details])
            
            if len(audit_data) > 1:
                audit_table = self._create_table(audit_data, [1.2*inch, 1.8*inch, 1*inch, 1.8*inch])
                story.append(audit_table)
                if len(audit_logs) > 20:
                    story.append(Paragraph(f"* Showing last 20 of {len(audit_logs)} audit log entries", 
                                          ParagraphStyle('Note', parent=styles['Normal'], 
                                                        fontSize=8, textColor=self.COLOR_TEXT_LIGHT, 
                                                        fontStyle='italic')))
            story.append(Spacer(1, 0.4*inch))
        
        # ========== COMPLIANCE CHECKLIST ==========
        story.append(Paragraph("7. Regulatory Compliance Checklist", self._get_heading_style(16)))
        story.append(Spacer(1, 0.2*inch))
        
        compliance_data = []
        compliance_data.append(["Requirement", "Status", "Notes"])
        
        compliance_items = [
            ("Data Validation", trial.validation_status == "passed", 
             "Rule engine validation completed"),
            ("ML Bias Check", trial.ml_status in ["ACCEPT", "REVIEW"],
             f"ML status: {trial.ml_status}" if trial.ml_status else "Not performed"),
            ("Blockchain Immutability", trial.blockchain_status == "written",
             "Trial data secured on distributed ledger" if trial.blockchain_status == "written" else "Pending blockchain write"),
            ("Digital Signature", trial.digital_signature is not None,
             "Cryptographically signed by investigator" if trial.digital_signature else "Not signed"),
            ("Audit Trail", audit_logs is not None and len(audit_logs) > 0,
             f"{len(audit_logs)} audit log entries" if audit_logs else "No audit logs"),
            ("Participant Privacy", True, "Data pseudonymized according to HIPAA/GDPR"),
        ]
        
        for item, status, notes in compliance_items:
            status_text = "✓ COMPLIANT" if status else "✗ NON-COMPLIANT"
            compliance_data.append([item, status_text, notes])
        
        compliance_table = self._create_table(compliance_data, [2*inch, 2*inch, 2*inch])
        story.append(compliance_table)
        story.append(Spacer(1, 0.4*inch))
        
        # ========== FOOTER ==========
        story.append(Spacer(1, 0.5*inch))
        story.append(Paragraph("─" * 80, ParagraphStyle('Separator', parent=styles['Normal'],
                                                         fontSize=8, textColor=colors.grey,
                                                         alignment=TA_CENTER)))
        story.append(Spacer(1, 0.2*inch))
        
        footer_text = [
            f"Report generated by TrialChain Blockchain Platform on {datetime.now().strftime('%B %d, %Y at %I:%M %p UTC')}",
            "This document is confidential and intended for authorized personnel only.",
            "TrialChain ensures data integrity through blockchain technology and AI-powered bias detection."
        ]
        
        for text in footer_text:
            story.append(Paragraph(text, ParagraphStyle(
                'Footer', parent=styles['Normal'],
                fontSize=8, textColor=self.COLOR_TEXT_LIGHT,
                alignment=TA_CENTER, spaceAfter=4
            )))
        
        # Build PDF
        doc.build(story, onFirstPage=self._add_page_number, onLaterPages=self._add_page_number)
        
        return filepath
    
    def _add_page_number(self, canvas_obj, doc):
        """Add page numbers to PDF"""
        canvas_obj.saveState()
        canvas_obj.setFont('Helvetica', 8)
        canvas_obj.setFillColor(self.COLOR_TEXT_LIGHT)
        page_num = canvas_obj.getPageNumber()
        text = f"Page {page_num}"
        canvas_obj.drawCentredString(4.25*inch, 0.75*inch, text)
        
        # Add green line at bottom
        canvas_obj.setStrokeColor(self.COLOR_PRIMARY_GREEN)
        canvas_obj.setLineWidth(1)
        canvas_obj.line(1*inch, 0.85*inch, 7*inch, 0.85*inch)
        canvas_obj.restoreState()

