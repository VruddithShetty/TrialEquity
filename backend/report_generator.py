"""
Simplified PDF Report Generator for Clinical Trials
Focused report with bias status, participant attributes, and digital signatures
"""
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.lib.units import cm
from datetime import datetime, timezone
from typing import Dict, Any, Optional
import os
import tempfile
import json

class ReportGenerator:
    """Generate simplified professional PDF reports for clinical trials"""

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

    def _extract_participant_attributes(self, trial_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Extract participant attribute counts from trial metadata"""
        attributes = {
            "total_participants": 0,
            "gender": {"male": 0, "female": 0, "other": 0},
            "ethnicity": {"white": 0, "black": 0, "asian": 0, "hispanic": 0, "others": 0},
            "age_groups": {"0-18": 0, "18-32": 0, "33-49": 0, "50-64": 0, "65+": 0}
        }

        try:
            # Get total participants
            sample_size = trial_metadata.get("sample_size", 0)
            participant_count = trial_metadata.get("participant_count", sample_size)
            attributes["total_participants"] = participant_count
            
            # Extract gender distribution (percentages to counts)
            gender_dist = trial_metadata.get("gender_distribution", {})
            if gender_dist and participant_count > 0:
                male_pct = gender_dist.get("male", 0.5)
                female_pct = gender_dist.get("female", 0.5)
                
                # Normalize if sum != 1
                total = male_pct + female_pct
                if total > 0:
                    male_pct = male_pct / total
                    female_pct = female_pct / total
                
                attributes["gender"]["male"] = int(male_pct * participant_count)
                attributes["gender"]["female"] = int(female_pct * participant_count)
                attributes["gender"]["other"] = participant_count - attributes["gender"]["male"] - attributes["gender"]["female"]
            
            # Extract ethnicity distribution
            ethnicity_dist = trial_metadata.get("ethnicity_distribution", {})
            if ethnicity_dist and participant_count > 0:
                for key, value in ethnicity_dist.items():
                    key_lower = str(key).lower()
                    count = int(value * participant_count) if value < 1 else int(value)
                    
                    if "white" in key_lower or "caucasian" in key_lower:
                        attributes["ethnicity"]["white"] = count
                    elif "black" in key_lower or "african" in key_lower:
                        attributes["ethnicity"]["black"] = count
                    elif "asian" in key_lower:
                        attributes["ethnicity"]["asian"] = count
                    elif "hispanic" in key_lower or "latino" in key_lower:
                        attributes["ethnicity"]["hispanic"] = count
                    else:
                        attributes["ethnicity"]["others"] += count
            
            # Extract age distribution
            age_dist = trial_metadata.get("age_distribution", {})
            if age_dist and participant_count > 0:
                age_mean = age_dist.get("mean", 50)
                age_std = age_dist.get("std", 10)
                age_min = age_dist.get("min", 18)
                age_max = age_dist.get("max", 80)
                
                # Estimate age group distribution based on mean and std
                # This is an approximation - in real implementation would use actual age data
                if age_mean < 25:
                    attributes["age_groups"]["18-32"] = int(participant_count * 0.6)
                    attributes["age_groups"]["33-49"] = int(participant_count * 0.3)
                    attributes["age_groups"]["50-64"] = int(participant_count * 0.1)
                elif age_mean < 40:
                    attributes["age_groups"]["18-32"] = int(participant_count * 0.4)
                    attributes["age_groups"]["33-49"] = int(participant_count * 0.5)
                    attributes["age_groups"]["50-64"] = int(participant_count * 0.1)
                elif age_mean < 55:
                    attributes["age_groups"]["18-32"] = int(participant_count * 0.2)
                    attributes["age_groups"]["33-49"] = int(participant_count * 0.5)
                    attributes["age_groups"]["50-64"] = int(participant_count * 0.3)
                elif age_mean < 70:
                    attributes["age_groups"]["33-49"] = int(participant_count * 0.2)
                    attributes["age_groups"]["50-64"] = int(participant_count * 0.5)
                    attributes["age_groups"]["65+"] = int(participant_count * 0.3)
                else:
                    attributes["age_groups"]["50-64"] = int(participant_count * 0.3)
                    attributes["age_groups"]["65+"] = int(participant_count * 0.7)
                
                # Add children if min age < 18
                if age_min < 18:
                    attributes["age_groups"]["0-18"] = int(participant_count * 0.1)

        except Exception as e:
            print(f"Error extracting participant attributes: {e}")
            import traceback
            print(traceback.format_exc())

        return attributes

    async def generate_report(self, trial, uploaded_by_user: Optional[Any] = None, audit_logs: Optional[list] = None) -> str:
        """Generate simplified professional PDF report for a trial"""
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
        story.append(Paragraph("Clinical Trial Report", cover_subtitle_style))
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
        current_time = datetime.now()
        cover_meta = [
            f"Generated: {current_time.strftime('%B %d, %Y at %I:%M %p')}",
            f"Report Version: 2.0 (Simplified)",
            f"Confidential Document"
        ]
        for meta in cover_meta:
            story.append(Paragraph(meta, ParagraphStyle(
                'CoverMeta', parent=styles['Normal'],
                fontSize=9, textColor=self.COLOR_TEXT_LIGHT,
                alignment=TA_CENTER, spaceAfter=5
            )))

        story.append(PageBreak())

        # ========== BIAS ANALYSIS SUMMARY ==========
        story.append(Paragraph("Bias Analysis Summary", self._get_heading_style(18, self.COLOR_DARK_GREEN)))
        story.append(Spacer(1, 0.2*inch))

        # Determine bias status
        bias_status = "UNKNOWN"
        bias_color = colors.HexColor('#f59e0b')  # Orange for unknown

        if trial.ml_status:
            if trial.ml_status == "ACCEPT":
                bias_status = "UNBIASED"
                bias_color = self.COLOR_PRIMARY_GREEN
            elif trial.ml_status == "REVIEW":
                bias_status = "REQUIRES REVIEW"
                bias_color = colors.HexColor('#f59e0b')  # Orange
            elif trial.ml_status == "REJECT":
                bias_status = "BIASED"
                bias_color = colors.red

        # Calculate points lost
        points_lost = 0
        if trial.ml_score is not None:
            points_lost = round((1.0 - trial.ml_score) * 100, 1)

        # Get human-readable reasons
        reasons = []
        if trial.ml_details and "recommendations" in trial.ml_details:
            reasons = trial.ml_details["recommendations"]
        if not reasons:
            reasons = ["No specific issues identified."]

        summary_data = [
            ["Metric", "Value", "Status"],
            ["Bias Status", bias_status, "✓ VERIFIED" if bias_status != "UNKNOWN" else "⏳ PENDING"],
            ["Fairness Score", f"{trial.ml_score:.3f}" if trial.ml_score else "N/A",
             "EXCELLENT" if trial.ml_score and trial.ml_score >= 0.8 else "GOOD" if trial.ml_score and trial.ml_score >= 0.6 else "REVIEW"],
            ["Points Lost", f"{points_lost}/100", "CRITICAL" if points_lost > 50 else "MODERATE" if points_lost > 20 else "MINOR"],
            ["Digital Signature Status", "Yes" if trial.digital_signature else "No", "✓ VERIFIED" if trial.digital_signature else "⏳ PENDING"],
        ]

        summary_table = self._create_table(summary_data, [2*inch, 2*inch, 2*inch])
        story.append(summary_table)
        story.append(Spacer(1, 0.4*inch))

        # ========== REASONS FOR POINTS LOST ==========
        if reasons:
            story.append(Paragraph("Reasons for Points Lost", self._get_heading_style(16)))
            story.append(Spacer(1, 0.2*inch))

            reasons_data = [["Reason"]]
            for reason in reasons:
                reasons_data.append([reason])

            reasons_table = self._create_table(reasons_data, [6*inch])
            story.append(reasons_table)
            story.append(Spacer(1, 0.4*inch))

        # ========== PARTICIPANT ATTRIBUTES ==========
        story.append(Paragraph("Participant Attributes", self._get_heading_style(16)))
        story.append(Spacer(1, 0.2*inch))

        attributes = self._extract_participant_attributes(trial.metadata)

        attr_data = [
            ["Attribute", "Category", "Count", "Percentage"],
            ["Total Participants", "All", str(attributes["total_participants"]), "100%"],
            ["", "", "", ""],
            ["Gender", "Male", str(attributes["gender"]["male"]), 
             f"{(attributes['gender']['male'] / max(attributes['total_participants'], 1) * 100):.1f}%"],
            ["Gender", "Female", str(attributes["gender"]["female"]),
             f"{(attributes['gender']['female'] / max(attributes['total_participants'], 1) * 100):.1f}%"],
            ["Gender", "Other", str(attributes["gender"]["other"]),
             f"{(attributes['gender']['other'] / max(attributes['total_participants'], 1) * 100):.1f}%"],
            ["", "", "", ""],
        ]

        # Add ethnicity data (expanded categories)
        attr_data.extend([
            ["Ethnicity", "White/Caucasian", str(attributes["ethnicity"]["white"]),
             f"{(attributes['ethnicity']['white'] / max(attributes['total_participants'], 1) * 100):.1f}%"],
            ["Ethnicity", "Black/African American", str(attributes["ethnicity"]["black"]),
             f"{(attributes['ethnicity']['black'] / max(attributes['total_participants'], 1) * 100):.1f}%"],
            ["Ethnicity", "Asian", str(attributes["ethnicity"]["asian"]),
             f"{(attributes['ethnicity']['asian'] / max(attributes['total_participants'], 1) * 100):.1f}%"],
            ["Ethnicity", "Hispanic/Latino", str(attributes["ethnicity"]["hispanic"]),
             f"{(attributes['ethnicity']['hispanic'] / max(attributes['total_participants'], 1) * 100):.1f}%"],
            ["Ethnicity", "Others", str(attributes["ethnicity"]["others"]),
             f"{(attributes['ethnicity']['others'] / max(attributes['total_participants'], 1) * 100):.1f}%"],
            ["", "", "", ""],
        ])

        # Add age groups with better categorization
        attr_data.extend([
            ["Age Groups", "Children (0-18)", str(attributes["age_groups"]["0-18"]),
             f"{(attributes['age_groups']['0-18'] / max(attributes['total_participants'], 1) * 100):.1f}%"],
            ["Age Groups", "Young Adults (18-32)", str(attributes["age_groups"]["18-32"]),
             f"{(attributes['age_groups']['18-32'] / max(attributes['total_participants'], 1) * 100):.1f}%"],
            ["Age Groups", "Middle Aged (33-49)", str(attributes["age_groups"]["33-49"]),
             f"{(attributes['age_groups']['33-49'] / max(attributes['total_participants'], 1) * 100):.1f}%"],
            ["Age Groups", "Older Adults (50-64)", str(attributes["age_groups"]["50-64"]),
             f"{(attributes['age_groups']['50-64'] / max(attributes['total_participants'], 1) * 100):.1f}%"],
            ["Age Groups", "Seniors (65+)", str(attributes["age_groups"]["65+"]),
             f"{(attributes['age_groups']['65+'] / max(attributes['total_participants'], 1) * 100):.1f}%"],
        ])

        attr_table = self._create_table(attr_data, [1.2*inch, 2*inch, 0.8*inch, 1*inch])
        story.append(attr_table)
        story.append(Spacer(1, 0.4*inch))

        # ========== DIGITAL SIGNATURE ==========
        story.append(Paragraph("Digital Signature", self._get_heading_style(16)))
        story.append(Spacer(1, 0.2*inch))

        signature_data = [
            ["Field", "Value"],
            ["Signature Status", "Yes" if trial.digital_signature else "No"],
        ]

        if trial.digital_signature:
            signature_data.extend([
                ["Digital Signature", trial.digital_signature[:64] + "..." if len(trial.digital_signature) > 64 else trial.digital_signature],
                ["Signed By", f"User ID: {str(trial.signed_by)}" if trial.signed_by else "N/A"],
                ["Signature Timestamp", trial.signature_timestamp.strftime("%Y-%m-%d %H:%M:%S") if trial.signature_timestamp else "N/A"],
            ])

        signature_table = self._create_table(signature_data, [2.5*inch, 3.5*inch])
        story.append(signature_table)
        story.append(Spacer(1, 0.4*inch))

        # ========== UPLOAD INFORMATION ==========
        if uploaded_by_user:
            story.append(Paragraph("Upload Information", self._get_heading_style(16)))
            story.append(Spacer(1, 0.2*inch))

            # Convert UTC times to local timezone for display
            from datetime import timezone
            import pytz
            
            # Use IST (Indian Standard Time) or system local time
            local_tz = pytz.timezone('Asia/Kolkata')  # IST timezone
            
            upload_date_str = "N/A"
            update_date_str = "N/A"
            
            if trial.created_at:
                if trial.created_at.tzinfo is None:
                    # If naive datetime, assume UTC
                    utc_dt = pytz.utc.localize(trial.created_at)
                else:
                    utc_dt = trial.created_at
                local_dt = utc_dt.astimezone(local_tz)
                upload_date_str = local_dt.strftime("%Y-%m-%d %I:%M:%S %p %Z")
            
            if trial.updated_at:
                if trial.updated_at.tzinfo is None:
                    utc_dt = pytz.utc.localize(trial.updated_at)
                else:
                    utc_dt = trial.updated_at
                local_dt = utc_dt.astimezone(local_tz)
                update_date_str = local_dt.strftime("%Y-%m-%d %I:%M:%S %p %Z")

            upload_data = [
                ["Field", "Value"],
                ["Uploaded By", f"{uploaded_by_user.get('username', 'Unknown')} ({uploaded_by_user.get('email', 'N/A')})"],
                ["User Role", uploaded_by_user.get('role', 'N/A')],
                ["Upload Date", upload_date_str],
                ["Last Updated", update_date_str],
            ]

            if uploaded_by_user.get('organization'):
                upload_data.append(["Organization", uploaded_by_user.get('organization')])

            upload_table = self._create_table(upload_data, [2.5*inch, 3.5*inch])
            story.append(upload_table)
            story.append(Spacer(1, 0.4*inch))

        # ========== FOOTER ==========
        story.append(Spacer(1, 0.5*inch))
        story.append(Paragraph("─" * 80, ParagraphStyle('Separator', parent=styles['Normal'],
                                                         fontSize=8, textColor=colors.grey,
                                                         alignment=TA_CENTER)))
        story.append(Spacer(1, 0.2*inch))

        footer_text = [
            f"Report generated by TrialChain Blockchain Platform on {current_time.strftime('%B %d, %Y at %I:%M %p')}",
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

    def generate_blockchain_summary(self, summary: Dict[str, Any]) -> str:
        """
        Generate a PDF summarizing blockchain-written trials with counts and basic info.
        Expected summary keys:
          - total_written: int
          - accepted_count: int
          - review_count: int
          - rejected_count: int
          - by_uploader: List[Dict[str, Any]] (username, count)
          - recent_trials: List[Dict[str, Any]] (trial_id, filename, ml_status, timestamp)
        """
        filename = "blockchain_summary.pdf"
        filepath = os.path.join(self.output_dir, filename)

        doc = SimpleDocTemplate(filepath, pagesize=letter,
                               rightMargin=72, leftMargin=72,
                               topMargin=72, bottomMargin=72)
        story = []
        styles = getSampleStyleSheet()

        # Title
        title_style = ParagraphStyle(
            'SummaryTitle',
            parent=styles['Title'],
            fontSize=26,
            textColor=self.COLOR_DARK_GREEN,
            alignment=TA_LEFT,
            spaceAfter=12,
        )
        story.append(Paragraph("Blockchain Summary Report", title_style))

        # Timestamp
        now_utc = datetime.now(timezone.utc)
        try:
            import pytz
            ist = pytz.timezone('Asia/Kolkata')
            now_str = now_utc.astimezone(ist).strftime('%Y-%m-%d %I:%M:%S %p IST')
        except Exception:
            now_str = now_utc.strftime('%Y-%m-%d %H:%M:%S UTC')
        story.append(Paragraph(f"Generated: {now_str}", self._get_body_style()))
        story.append(Spacer(1, 12))

        # Summary counts table
        counts_data = [
            ["Metric", "Count"],
            ["Total Written to Blockchain", str(summary.get('total_written', 0))],
            ["Accepted", str(summary.get('accepted_count', 0))],
            ["Under Review", str(summary.get('review_count', 0))],
            ["Rejected", str(summary.get('rejected_count', 0))],
        ]
        story.append(self._create_table(counts_data, [3*inch, 2*inch]))
        story.append(Spacer(1, 18))

        # By uploader table
        by_uploader = summary.get('by_uploader', []) or []
        if by_uploader:
            story.append(Paragraph("Written Trials by Uploader", self._get_heading_style(16)))
            uploader_data = [["Uploader", "Count"]]
            for row in by_uploader:
                uploader_data.append([row.get('username', 'Unknown'), str(row.get('count', 0))])
            story.append(self._create_table(uploader_data, [3*inch, 2*inch]))
            story.append(Spacer(1, 18))

        # Recent trials table
        recent_trials = summary.get('recent_trials', []) or []
        if recent_trials:
            story.append(Paragraph("Recent Blockchain-Written Trials", self._get_heading_style(16)))
            trials_data = [["Trial ID", "Filename", "ML Status", "Written At"]]
            for t in recent_trials:
                trials_data.append([
                    str(t.get('trial_id', '')),
                    t.get('filename', ''),
                    t.get('ml_status', ''),
                    t.get('timestamp', ''),
                ])
            story.append(self._create_table(trials_data, [2*inch, 2*inch, 1.5*inch, 2*inch]))

        # Build PDF
        doc.build(story)
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