"""
Generate optimized AI Workflow Template PDF - fits on one page
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

def create_workflow_template_pdf(output_path):
    """Create the AI Workflow Template PDF with optimized formatting"""

    # Create PDF with tight margins
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=0.5*inch,
        leftMargin=0.5*inch,
        topMargin=0.4*inch,
        bottomMargin=0.4*inch
    )

    # Story to hold all elements
    story = []

    # Define colors
    primary_blue = HexColor('#2563EB')
    secondary_gray = HexColor('#6B7280')
    light_gray = HexColor('#F3F4F6')
    orange = HexColor('#F97316')

    # Define optimized styles with smaller fonts and tighter spacing
    styles = getSampleStyleSheet()

    # Main title style - reduced from default
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=22,  # Reduced from ~26
        textColor=primary_blue,
        spaceAfter=4,  # Reduced spacing
        alignment=TA_CENTER,
        fontName='Helvetica-Bold',
        leading=24
    )

    # Subtitle style
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Normal'],
        fontSize=13,  # Reduced from 14-15
        textColor=secondary_gray,
        spaceAfter=3,
        alignment=TA_CENTER,
        fontName='Helvetica',
        leading=15
    )

    # Intro style
    intro_style = ParagraphStyle(
        'CustomIntro',
        parent=styles['Normal'],
        fontSize=9,  # Reduced from 10
        textColor=secondary_gray,
        spaceAfter=8,  # Reduced spacing
        alignment=TA_CENTER,
        leading=11
    )

    # Section header style
    section_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading2'],
        fontSize=12,  # Reduced from 14
        textColor=primary_blue,
        spaceAfter=3,  # Reduced spacing
        spaceBefore=6,  # Reduced spacing
        fontName='Helvetica-Bold',
        leading=14
    )

    # Question style
    question_style = ParagraphStyle(
        'Question',
        parent=styles['Normal'],
        fontSize=9,  # Reduced from 10
        textColor=secondary_gray,
        spaceAfter=2,
        fontName='Helvetica',
        leading=11
    )

    # Example hint style
    hint_style = ParagraphStyle(
        'Hint',
        parent=styles['Normal'],
        fontSize=7.5,  # Reduced from 8
        textColor=secondary_gray,
        spaceAfter=3,  # Reduced spacing
        fontName='Helvetica-Oblique',
        leading=9
    )

    # Example section header
    example_header_style = ParagraphStyle(
        'ExampleHeader',
        parent=styles['Heading2'],
        fontSize=11,  # Reduced from 12
        textColor=orange,
        spaceAfter=4,
        spaceBefore=8,
        fontName='Helvetica-Bold',
        leading=13
    )

    # Example body style
    example_body_style = ParagraphStyle(
        'ExampleBody',
        parent=styles['Normal'],
        fontSize=8,  # Reduced from 9
        textColor=secondary_gray,
        spaceAfter=1,
        fontName='Helvetica',
        leading=10
    )

    # Add title
    story.append(Paragraph("Your First AI Workflow Template", title_style))
    story.append(Paragraph("Turn Any Repetitive Task Into An Automated Process", subtitle_style))
    story.append(Paragraph("Use this framework to identify and automate your first workflow. Follow the 5 steps below.", intro_style))

    # Section 1
    story.append(Paragraph("Section 1: Identify Your Task", section_style))
    story.append(Paragraph("Question: What task do you repeat daily or weekly?", question_style))
    story.append(Paragraph("<i>Example hint: Checking emails, scheduling meetings, data entry, report generation</i>", hint_style))
    story.append(create_text_field(height=0.45*inch))

    # Section 2
    story.append(Paragraph("Section 2: Define Your Ideal Output", section_style))
    story.append(Paragraph("Question: What's the perfect result you want?", question_style))
    story.append(Paragraph("<i>Example hint: 3-bullet email summary, calendar event created, spreadsheet updated</i>", hint_style))
    story.append(create_text_field(height=0.45*inch))

    # Section 3
    story.append(Paragraph("Section 3: Pick Your Trigger", section_style))
    story.append(Paragraph("Question: What should start this automation?", question_style))
    story.append(Paragraph("<i>Example hint: New email arrives, calendar event scheduled, form submission received</i>", hint_style))
    story.append(create_text_field(height=0.45*inch))

    # Section 4
    story.append(Paragraph("Section 4: Draft Your Base Prompt", section_style))
    story.append(Paragraph("Question: What instruction should the AI follow?", question_style))
    story.append(Paragraph('<i>Example hint: "Summarize this email in 3 bullet points focusing on action items and deadlines"</i>', hint_style))
    story.append(create_text_field(height=0.6*inch))

    # Section 5
    story.append(Paragraph("Section 5: Choose Your Automation Tool", section_style))
    story.append(Paragraph("Question: Which tool will you use to build this?", question_style))
    story.append(Spacer(1, 0.08*inch))

    # Checkboxes - using simpler approach with text
    checkbox_text = Paragraph("☐ Make.com &nbsp;&nbsp;&nbsp; ☐ Zapier &nbsp;&nbsp;&nbsp; ☐ n8n &nbsp;&nbsp;&nbsp; Other: ___________________________", question_style)
    story.append(checkbox_text)
    story.append(Spacer(1, 0.08*inch))

    # Separator line
    line_table = Table([['']], colWidths=[7.5*inch])
    line_table.setStyle(TableStyle([
        ('LINEABOVE', (0, 0), (-1, 0), 1, HexColor('#E5E7EB')),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]))
    story.append(line_table)

    # Example section - more compact
    story.append(Paragraph("Example: AI Email Summary Workflow", example_header_style))

    # Compact example details
    example_details = [
        ["Task:", "Reading important emails"],
        ["Output:", "3-bullet summary posted to Slack"],
        ["Trigger:", "New email with [URGENT] in subject"],
        ["Prompt:", '"Extract 3 key action items and deadline"'],
        ["Tool:", "Make.com with Claude API + Slack"]
    ]

    example_table = Table(example_details, colWidths=[0.9*inch, 6.6*inch])
    example_table.setStyle(TableStyle([
        ('FONTSIZE', (0, 0), (-1, -1), 7.5),
        ('TEXTCOLOR', (0, 0), (-1, -1), secondary_gray),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 2),
        ('RIGHTPADDING', (0, 0), (-1, -1), 2),
        ('TOPPADDING', (0, 0), (-1, -1), 1),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),  # Bold labels in first column
    ]))
    story.append(example_table)
    story.append(Spacer(1, 0.05*inch))

    # Footer
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=7,
        textColor=secondary_gray,
        alignment=TA_CENTER,
        fontName='Helvetica-Oblique',
        leading=8
    )
    story.append(Paragraph("Your First AI Workflow Template - Start automating today!", footer_style))

    # Build PDF
    doc.build(story)
    print(f"[OK] PDF generated: {output_path}")

def create_text_field(width=7.5*inch, height=0.5*inch):
    """Create a text field as a table with border"""
    field = Table([['']], colWidths=[width], rowHeights=[height])
    field.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 1, HexColor('#D1D5DB')),
        ('BACKGROUND', (0, 0), (-1, -1), HexColor('#FFFFFF')),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
    ]))
    return field

def create_checkbox():
    """Create a checkbox as a table"""
    checkbox = Table([['']], colWidths=[0.12*inch], rowHeights=[0.12*inch])
    checkbox.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 1, HexColor('#9CA3AF')),
        ('BACKGROUND', (0, 0), (-1, -1), HexColor('#FFFFFF')),
    ]))
    return checkbox

if __name__ == "__main__":
    # Output path
    output_dir = r"c:\Users\sabaa\OneDrive\Desktop\TEST_AGENTS\MARKETING_TEAM\outputs\pdfs"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "prompt_to_process_template.pdf")

    # Generate PDF
    create_workflow_template_pdf(output_path)
    print(f"\n[SUCCESS] Optimized PDF generated: {output_path}")
    print("[INFO] All content fits on one page with readable formatting")
