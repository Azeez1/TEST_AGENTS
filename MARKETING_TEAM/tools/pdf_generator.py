"""
PDF Generation Tool
Creates professional PDFs for whitepapers, lead magnets, reports
"""

from claude_agent_sdk import tool
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Image, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
import json
import os
from pathlib import Path
from datetime import datetime


@tool(
    "generate_pdf",
    "Generate professional PDF document (whitepaper, lead magnet, report)",
    {
        "title": str,
        "subtitle": str,
        "content": list,  # List of sections: [{"type": "heading", "text": "..."}, {"type": "paragraph", "text": "..."}, ...]
        "author": str,
        "company": str,
        "logo_path": str,  # Optional
        "filename": str
    }
)
async def generate_pdf(args):
    """
    Generate professional PDF document
    """

    title = args["title"]
    subtitle = args.get("subtitle", "")
    content = args["content"]
    author = args.get("author", "")
    company = args.get("company", "")
    logo_path = args.get("logo_path", "")
    filename = args.get("filename", "document.pdf")

    # Ensure output directory exists
    output_dir = Path("output/pdfs")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Full output path
    output_path = output_dir / filename

    try:
        # Create PDF
        doc = SimpleDocTemplate(
            str(output_path),
            pagesize=letter,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch
        )

        # Container for PDF elements
        elements = []

        # Define styles
        styles = getSampleStyleSheet()

        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=28,
            textColor=colors.HexColor('#0066CC'),
            spaceAfter=12,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )

        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#666666'),
            spaceAfter=20,
            alignment=TA_CENTER,
            fontName='Helvetica'
        )

        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=18,
            textColor=colors.HexColor('#0066CC'),
            spaceAfter=12,
            spaceBefore=20,
            fontName='Helvetica-Bold'
        )

        body_style = ParagraphStyle(
            'CustomBody',
            parent=styles['BodyText'],
            fontSize=11,
            textColor=colors.black,
            spaceAfter=12,
            alignment=TA_JUSTIFY,
            fontName='Helvetica',
            leading=16
        )

        # Add logo if provided
        if logo_path and os.path.exists(logo_path):
            logo = Image(logo_path, width=2*inch, height=0.5*inch)
            elements.append(logo)
            elements.append(Spacer(1, 0.3*inch))

        # Add title page
        elements.append(Spacer(1, 2*inch))
        elements.append(Paragraph(title, title_style))

        if subtitle:
            elements.append(Spacer(1, 0.2*inch))
            elements.append(Paragraph(subtitle, subtitle_style))

        elements.append(Spacer(1, 0.5*inch))

        # Add author/company info
        if author or company:
            info_text = ""
            if author:
                info_text += f"By {author}"
            if company:
                if author:
                    info_text += f" | {company}"
                else:
                    info_text += company

            info_style = ParagraphStyle(
                'Info',
                parent=styles['Normal'],
                fontSize=12,
                textColor=colors.HexColor('#666666'),
                alignment=TA_CENTER
            )
            elements.append(Paragraph(info_text, info_style))

        # Add date
        date_text = datetime.now().strftime("%B %Y")
        elements.append(Spacer(1, 0.2*inch))
        elements.append(Paragraph(date_text, info_style))

        # Page break after cover
        elements.append(PageBreak())

        # Add content
        for section in content:
            section_type = section.get("type", "paragraph")
            text = section.get("text", "")

            if section_type == "heading":
                elements.append(Paragraph(text, heading_style))

            elif section_type == "subheading":
                subheading_style = ParagraphStyle(
                    'Subheading',
                    parent=styles['Heading3'],
                    fontSize=14,
                    textColor=colors.HexColor('#333333'),
                    spaceAfter=10,
                    spaceBefore=15,
                    fontName='Helvetica-Bold'
                )
                elements.append(Paragraph(text, subheading_style))

            elif section_type == "paragraph":
                elements.append(Paragraph(text, body_style))

            elif section_type == "bullet_list":
                items = section.get("items", [])
                for item in items:
                    bullet_text = f"• {item}"
                    elements.append(Paragraph(bullet_text, body_style))
                elements.append(Spacer(1, 0.1*inch))

            elif section_type == "numbered_list":
                items = section.get("items", [])
                for i, item in enumerate(items, 1):
                    numbered_text = f"{i}. {item}"
                    elements.append(Paragraph(numbered_text, body_style))
                elements.append(Spacer(1, 0.1*inch))

            elif section_type == "quote":
                quote_style = ParagraphStyle(
                    'Quote',
                    parent=styles['BodyText'],
                    fontSize=12,
                    textColor=colors.HexColor('#666666'),
                    spaceAfter=12,
                    leftIndent=0.5*inch,
                    rightIndent=0.5*inch,
                    fontName='Helvetica-Oblique'
                )
                elements.append(Paragraph(f'"{text}"', quote_style))

            elif section_type == "spacer":
                height = section.get("height", 0.2)
                elements.append(Spacer(1, height*inch))

            elif section_type == "page_break":
                elements.append(PageBreak())

            elif section_type == "table":
                table_data = section.get("data", [])
                if table_data:
                    table = Table(table_data)
                    table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0066CC')),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, 0), 12),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black)
                    ]))
                    elements.append(table)
                    elements.append(Spacer(1, 0.2*inch))

        # Add footer/CTA on last page
        elements.append(Spacer(1, 1*inch))
        cta_style = ParagraphStyle(
            'CTA',
            parent=styles['Normal'],
            fontSize=14,
            textColor=colors.HexColor('#0066CC'),
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )

        if company:
            elements.append(Paragraph(f"Learn more at {company}", cta_style))

        # Build PDF
        doc.build(elements)

        result = {
            "status": "success",
            "title": title,
            "filename": filename,
            "output_path": str(output_path),
            "file_size": f"{os.path.getsize(output_path) / 1024:.1f} KB",
            "pages": len(content) + 1,  # Approximate
            "created_at": datetime.now().isoformat(),
            "next_step": "Use upload_to_google_drive tool to upload and get shareable link"
        }

        return {
            "content": [{
                "type": "text",
                "text": json.dumps(result, indent=2)
            }]
        }

    except Exception as e:
        return {
            "content": [{
                "type": "text",
                "text": f"Error generating PDF: {str(e)}"
            }]
        }


@tool(
    "create_lead_magnet_pdf",
    "Create a lead magnet PDF (checklist, template, guide)",
    {
        "type": str,  # "checklist", "template", "guide"
        "title": str,
        "items": list,  # List of checklist items or guide sections
        "filename": str
    }
)
async def create_lead_magnet_pdf(args):
    """
    Create a quick lead magnet PDF
    """
    magnet_type = args["type"]
    title = args["title"]
    items = args["items"]
    filename = args.get("filename", "lead-magnet.pdf")

    # Structure content based on type
    content = []

    if magnet_type == "checklist":
        content.append({
            "type": "heading",
            "text": "Your Checklist:"
        })
        content.append({"type": "spacer", "height": 0.3})

        for item in items:
            content.append({
                "type": "paragraph",
                "text": f"☐ {item}"
            })

    elif magnet_type == "template":
        content.append({
            "type": "heading",
            "text": "Template Instructions:"
        })
        for i, item in enumerate(items, 1):
            content.append({
                "type": "subheading",
                "text": f"Step {i}"
            })
            content.append({
                "type": "paragraph",
                "text": item
            })

    elif magnet_type == "guide":
        for item in items:
            if isinstance(item, dict):
                content.append({
                    "type": "heading",
                    "text": item.get("section", "")
                })
                content.append({
                    "type": "paragraph",
                    "text": item.get("content", "")
                })
            else:
                content.append({
                    "type": "paragraph",
                    "text": str(item)
                })

    # Call main PDF generator
    return await generate_pdf({
        "title": title,
        "subtitle": f"{magnet_type.title()} for Marketing Success",
        "content": content,
        "filename": filename
    })
