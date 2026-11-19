import os
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image as RLImage,
    KeepTogether,
    HRFlowable
)
from reportlab.lib.units import inch

from backend.config import BASE_DIR

def generate_pdf_report(inspection_data: Dict[str, Any], output_path: str) -> str:
    """
    Generates a professional engineering PDF report for a material inspection.
    """
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    # Custom typography
    navy_color = colors.HexColor("#0F172A")
    blue_color = colors.HexColor("#2563EB")
    charcoal_color = colors.HexColor("#1E293B")
    light_bg = colors.HexColor("#F8FAFC")
    border_color = colors.HexColor("#E2E8F0")

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=navy_color
    )

    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#64748B")
    )

    h2_style = ParagraphStyle(
        'SectionH2',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=navy_color,
        spaceBefore=10,
        spaceAfter=6
    )

    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=charcoal_color
    )

    badge_style = ParagraphStyle(
        'Badge',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=14,
        textColor=colors.white
    )

    disclaimer_style = ParagraphStyle(
        'Disclaimer',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=7.5,
        leading=11,
        textColor=colors.HexColor("#475569")
    )

    elements = []

    # 1. Header Banner
    header_data = [
        [
            Paragraph("<b>ConstructIQ Enterprise</b><br/><font size=8 color='#2563EB'>Material Quality & Reusability Assessment Report</font>", title_style),
            Paragraph(f"<b>REPORT ID:</b> {inspection_data.get('id', 'MAT-UNKNOWN')}<br/>"
                      f"<b>DATE:</b> {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}<br/>"
                      f"<b>STATUS:</b> {inspection_data.get('inspection_status', 'Verified').upper()}", subtitle_style)
        ]
    ]
    header_table = Table(header_data, colWidths=[4.0 * inch, 3.2 * inch])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(header_table)
    elements.append(HRFlowable(width="100%", thickness=1.5, color=blue_color, spaceBefore=4, spaceAfter=12))

    # 2. Executive Assessment Summary Box
    cond = inspection_data.get('condition', 'GOOD')
    recom = inspection_data.get('recommendation', 'REUSE')
    score = inspection_data.get('condition_score', 85.0)

    cond_color = colors.HexColor("#16A34A") if cond == "GOOD" else (colors.HexColor("#DC2626") if cond == "DAMAGED" else colors.HexColor("#D97706"))
    recom_color = colors.HexColor("#16A34A") if recom == "REUSE" else (colors.HexColor("#DC2626") if recom in ["REJECT", "RECYCLE"] else colors.HexColor("#D97706"))

    summary_data = [
        [
            Paragraph(f"<b>Material Category:</b> {inspection_data.get('material_category')}", body_style),
            Paragraph(f"<b>AI Confidence:</b> {inspection_data.get('confidence', 90)}%", body_style),
            Paragraph(f"<b>Condition Score:</b> {score} / 100", body_style),
        ],
        [
            Paragraph(f"<b>Project:</b> {inspection_data.get('project_name', 'EcoBuild')}", body_style),
            Paragraph(f"<b>Location:</b> {inspection_data.get('site_location', 'Yard A')}", body_style),
            Paragraph(f"<b>Quantity:</b> {inspection_data.get('quantity', 1)} {inspection_data.get('unit', 'pieces')}", body_style),
        ],
        [
            Paragraph(f"<font color='white'><b>CONDITION: {cond}</b></font>", badge_style),
            Paragraph(f"<font color='white'><b>RECOMMENDATION: {recom}</b></font>", badge_style),
            Paragraph(f"<b>Inspector:</b> {inspection_data.get('inspector_name', 'Lead Inspector')}", body_style),
        ]
    ]
    summary_table = Table(summary_data, colWidths=[2.5 * inch, 2.5 * inch, 2.2 * inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), light_bg),
        ('BOX', (0, 0), (-1, -1), 1, border_color),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, border_color),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('BACKGROUND', (0, 2), (0, 2), cond_color),
        ('BACKGROUND', (1, 2), (1, 2), recom_color),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 10))

    # 3. Visual Evidence (Original Image vs Annotated Defect Detection)
    elements.append(Paragraph("Visual Computer Vision Evidence", h2_style))

    orig_path = inspection_data.get('original_image_path', '')
    annot_path = inspection_data.get('annotated_image_path', '')

    # Resolve full file paths
    def get_full_img_path(rel_path: str):
        if not rel_path:
            return None
        clean = rel_path.lstrip("/").replace("/", os.sep)
        p1 = BASE_DIR / clean
        if p1.exists():
            return str(p1)
        p2 = Path(rel_path)
        if p2.exists():
            return str(p2)
        return None

    full_orig = get_full_img_path(orig_path)
    full_annot = get_full_img_path(annot_path)

    img_col_w = 3.55 * inch
    img_h = 2.4 * inch

    img_cells = []
    if full_orig and os.path.exists(full_orig):
        try:
            img_cells.append(RLImage(full_orig, width=img_col_w, height=img_h))
        except Exception:
            img_cells.append(Paragraph("[Original Image Unavailable]", body_style))
    else:
        img_cells.append(Paragraph("[Original Image Not Stored]", body_style))

    if full_annot and os.path.exists(full_annot):
        try:
            img_cells.append(RLImage(full_annot, width=img_col_w, height=img_h))
        except Exception:
            img_cells.append(Paragraph("[Annotated Vision Map Unavailable]", body_style))
    else:
        img_cells.append(Paragraph("[Defect Bounding Box Map Not Stored]", body_style))

    img_table_data = [
        [Paragraph("<b>Original Uploaded Material Image</b>", body_style), Paragraph("<b>AI Defect Localization Overlay (Bounding Boxes)</b>", body_style)],
        img_cells
    ]
    img_table = Table(img_table_data, colWidths=[3.6 * inch, 3.6 * inch])
    img_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('BOX', (0, 1), (0, 1), 1, border_color),
        ('BOX', (1, 1), (1, 1), 1, border_color),
        ('BACKGROUND', (0, 0), (-1, 0), light_bg),
    ]))
    elements.append(img_table)
    elements.append(Spacer(1, 10))

    # 4. Defect Detection Breakdown Table
    elements.append(Paragraph("Visible Defects Detected", h2_style))

    defects = inspection_data.get('defects', [])
    if isinstance(defects, str):
        try:
            defects = json.loads(defects)
        except Exception:
            defects = []

    # Normalize objects to dicts
    normalized_defects = []
    for d in defects:
        if hasattr(d, 'model_dump'):
            normalized_defects.append(d.model_dump())
        elif hasattr(d, 'dict'):
            normalized_defects.append(d.dict())
        elif isinstance(d, dict):
            normalized_defects.append(d)
        else:
            normalized_defects.append({"name": str(d), "severity": "Medium", "confidence": 80.0, "bbox": None, "description": ""})
    defects = normalized_defects

    defect_rows = [
        [
            Paragraph("<b>#</b>", body_style),
            Paragraph("<b>Defect Description</b>", body_style),
            Paragraph("<b>Severity</b>", body_style),
            Paragraph("<b>Confidence</b>", body_style),
            Paragraph("<b>Bounding Box (x, y, w, h)</b>", body_style)
        ]
    ]

    if not defects:
        defect_rows.append([
            Paragraph("1", body_style),
            Paragraph("No visible structural defects or surface deterioration detected.", body_style),
            Paragraph("None", body_style),
            Paragraph("100%", body_style),
            Paragraph("N/A", body_style)
        ])
    else:
        for idx, d in enumerate(defects, start=1):
            bbox = d.get('bbox', {})
            bbox_str = f"[{bbox.get('x',0)}, {bbox.get('y',0)}, {bbox.get('width',0)}x{bbox.get('height',0)}]" if bbox else "Full Area"
            sev = d.get('severity', 'Medium')
            sev_color = "#DC2626" if sev == "High" else ("#D97706" if sev == "Medium" else "#2563EB")
            defect_rows.append([
                Paragraph(str(idx), body_style),
                Paragraph(f"<b>{d.get('name', 'Defect')}</b><br/><font size=7 color='#64748B'>{d.get('description', '')}</font>", body_style),
                Paragraph(f"<font color='{sev_color}'><b>{sev}</b></font>", body_style),
                Paragraph(f"{d.get('confidence', 80)}%", body_style),
                Paragraph(bbox_str, body_style)
            ])

    defect_table = Table(defect_rows, colWidths=[0.35 * inch, 3.0 * inch, 1.1 * inch, 1.1 * inch, 1.65 * inch])
    defect_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), light_bg),
        ('BOX', (0, 0), (-1, -1), 1, border_color),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, border_color),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    elements.append(defect_table)
    elements.append(Spacer(1, 10))

    # 5. Recommendation & Next Steps Block
    elements.append(Paragraph("Intelligent Reusability Directive", h2_style))
    recom_box_data = [
        [
            Paragraph(f"<b>ENGINEERING RATIONALE:</b><br/>{inspection_data.get('recommendation_reason', 'Evaluation completed.')}<br/><br/>"
                      f"<b>ACTIONABLE NEXT STEPS:</b><br/>{inspection_data.get('suggested_next_step', 'Standard handling.')}", body_style)
        ]
    ]
    recom_table = Table(recom_box_data, colWidths=[7.2 * inch])
    recom_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), light_bg),
        ('BOX', (0, 0), (-1, -1), 1, border_color),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
    ]))
    elements.append(recom_table)
    elements.append(Spacer(1, 12))

    # 6. Safety Disclaimer & Sign-off Block
    elements.append(KeepTogether([
        Paragraph("<b>CRITICAL SAFETY DISCLAIMER:</b> "
                  "This report is produced by an automated computer vision inspection algorithm as a preliminary circular resource triage tool. "
                  "Photographic optical inspection alone CANNOT verify interior structural micro-fissures, tensile yield strength, concrete compressive strength, "
                  "or compliance with local building structural codes. All load-bearing items must undergo certified engineering NDT and structural sign-off before reuse.", disclaimer_style),
        Spacer(1, 10),
        Table([
            [
                Paragraph("<b>Inspector Sign-Off:</b> ___________________________", body_style),
                Paragraph("<b>Site Engineer Approval:</b> ___________________________", body_style),
                Paragraph(f"<b>Timestamp:</b> {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}", body_style)
            ]
        ], colWidths=[2.6 * inch, 2.6 * inch, 2.0 * inch])
    ]))

    doc.build(elements)
    return output_path
