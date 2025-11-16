"""
Create an interactive fillable PDF workbook: "Your First AI Workflow Template"

This script generates a professional workbook with text fields and checkboxes
for community members to design their first AI automation workflow.
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, black, white
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
import os

def draw_text_field(c, x, y, width, height, name, tooltip="", multiline=False):
    """Draw a text field form element"""
    # Draw border
    c.setStrokeColor(HexColor("#CCCCCC"))
    c.setLineWidth(1)
    c.rect(x, y, width, height, stroke=1, fill=0)

    # Add form field
    c.acroForm.textfield(
        name=name,
        tooltip=tooltip,
        x=x,
        y=y,
        width=width,
        height=height,
        borderColor=HexColor("#CCCCCC"),
        fillColor=white,
        textColor=black,
        forceBorder=True,
        fontSize=10,
        maxlen=500 if not multiline else 1000
    )

def draw_checkbox(c, x, y, size, name, label, label_x_offset=20):
    """Draw a checkbox with label"""
    # Draw checkbox
    c.acroForm.checkbox(
        name=name,
        tooltip=label,
        x=x,
        y=y,
        size=size,
        buttonStyle='check',
        borderColor=HexColor("#333333"),
        fillColor=white,
        textColor=black,
        forceBorder=True
    )

    # Draw label next to checkbox
    c.setFont("Helvetica", 10)
    c.setFillColor(black)
    c.drawString(x + label_x_offset, y + 2, label)

def create_fillable_workbook(output_path):
    """Create the interactive fillable PDF workbook"""

    # Create canvas
    c = canvas.Canvas(output_path, pagesize=letter)
    width, height = letter

    # Define colors
    brand_blue = HexColor("#2563EB")
    accent_orange = HexColor("#F97316")
    gray_light = HexColor("#F3F4F6")
    gray_dark = HexColor("#374151")

    # Set up fonts
    c.setTitle("Your First AI Workflow Template")

    # Header Section
    y_position = height - 60

    # Title
    c.setFont("Helvetica-Bold", 24)
    c.setFillColor(brand_blue)
    c.drawString(72, y_position, "Your First AI Workflow Template")

    y_position -= 30

    # Subtitle
    c.setFont("Helvetica", 14)
    c.setFillColor(gray_dark)
    c.drawString(72, y_position, "Turn Any Repetitive Task Into An Automated Process")

    y_position -= 25

    # Brief intro
    c.setFont("Helvetica", 10)
    c.setFillColor(gray_dark)
    intro_text = "Use this framework to identify and automate your first workflow. Follow the 5 steps below."
    c.drawString(72, y_position, intro_text)

    y_position -= 40

    # Section 1: Identify Your Task
    c.setFont("Helvetica-Bold", 14)
    c.setFillColor(brand_blue)
    c.drawString(72, y_position, "Section 1: Identify Your Task")

    y_position -= 20

    c.setFont("Helvetica", 10)
    c.setFillColor(gray_dark)
    c.drawString(72, y_position, "Question: What task do you repeat daily or weekly?")

    y_position -= 18

    # Example hint in smaller gray text
    c.setFont("Helvetica-Oblique", 8)
    c.setFillColor(HexColor("#6B7280"))
    c.drawString(72, y_position, "Example hint: Checking emails, scheduling meetings, data entry, report generation")

    y_position -= 10

    # Text field for Task
    draw_text_field(c, 72, y_position - 50, width - 144, 50, "task_field",
                   "Enter the task you repeat daily or weekly", multiline=True)

    y_position -= 70

    # Section 2: Define Your Ideal Output
    c.setFont("Helvetica-Bold", 14)
    c.setFillColor(brand_blue)
    c.drawString(72, y_position, "Section 2: Define Your Ideal Output")

    y_position -= 20

    c.setFont("Helvetica", 10)
    c.setFillColor(gray_dark)
    c.drawString(72, y_position, "Question: What's the perfect result you want?")

    y_position -= 18

    c.setFont("Helvetica-Oblique", 8)
    c.setFillColor(HexColor("#6B7280"))
    c.drawString(72, y_position, "Example hint: 3-bullet email summary, calendar event created, spreadsheet updated")

    y_position -= 10

    # Text field for Output
    draw_text_field(c, 72, y_position - 50, width - 144, 50, "output_field",
                   "Enter your ideal output", multiline=True)

    y_position -= 70

    # Section 3: Pick Your Trigger
    c.setFont("Helvetica-Bold", 14)
    c.setFillColor(brand_blue)
    c.drawString(72, y_position, "Section 3: Pick Your Trigger")

    y_position -= 20

    c.setFont("Helvetica", 10)
    c.setFillColor(gray_dark)
    c.drawString(72, y_position, "Question: What should start this automation?")

    y_position -= 18

    c.setFont("Helvetica-Oblique", 8)
    c.setFillColor(HexColor("#6B7280"))
    c.drawString(72, y_position, "Example hint: New email arrives, calendar event scheduled, form submission received")

    y_position -= 10

    # Text field for Trigger
    draw_text_field(c, 72, y_position - 35, width - 144, 35, "trigger_field",
                   "Enter what should trigger this automation", multiline=True)

    y_position -= 55

    # Section 4: Draft Your Base Prompt
    c.setFont("Helvetica-Bold", 14)
    c.setFillColor(brand_blue)
    c.drawString(72, y_position, "Section 4: Draft Your Base Prompt")

    y_position -= 20

    c.setFont("Helvetica", 10)
    c.setFillColor(gray_dark)
    c.drawString(72, y_position, "Question: What instruction should the AI follow?")

    y_position -= 18

    c.setFont("Helvetica-Oblique", 8)
    c.setFillColor(HexColor("#6B7280"))
    hint_text = 'Example hint: "Summarize this email in 3 bullet points focusing on action items and deadlines"'
    c.drawString(72, y_position, hint_text)

    y_position -= 10

    # Text field for Prompt (larger)
    draw_text_field(c, 72, y_position - 70, width - 144, 70, "prompt_field",
                   "Enter your AI prompt instruction", multiline=True)

    y_position -= 90

    # Section 5: Choose Your Automation Tool
    c.setFont("Helvetica-Bold", 14)
    c.setFillColor(brand_blue)
    c.drawString(72, y_position, "Section 5: Choose Your Automation Tool")

    y_position -= 20

    c.setFont("Helvetica", 10)
    c.setFillColor(gray_dark)
    c.drawString(72, y_position, "Question: Which tool will you use to build this?")

    y_position -= 25

    # Checkboxes for tools
    checkbox_y = y_position
    draw_checkbox(c, 90, checkbox_y, 12, "tool_make", "Make.com")
    draw_checkbox(c, 200, checkbox_y, 12, "tool_zapier", "Zapier")
    draw_checkbox(c, 290, checkbox_y, 12, "tool_n8n", "n8n")

    # Other field
    c.setFont("Helvetica", 10)
    c.setFillColor(gray_dark)
    c.drawString(380, checkbox_y + 2, "Other:")
    draw_text_field(c, 425, checkbox_y - 2, 120, 16, "tool_other", "Specify other tool")

    y_position -= 50

    # Separator line
    c.setStrokeColor(HexColor("#E5E7EB"))
    c.setLineWidth(1)
    c.line(72, y_position, width - 72, y_position)

    y_position -= 30

    # Example Workflow Section (Bottom)
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(accent_orange)
    c.drawString(72, y_position, "Example: AI Email Summary Workflow")

    y_position -= 18

    # Example content in smaller text
    c.setFont("Helvetica", 9)
    c.setFillColor(gray_dark)

    examples = [
        ("Task:", "Reading important emails"),
        ("Output:", "3-bullet summary posted to Slack"),
        ("Trigger:", "New email arrives in specific folder"),
        ("Prompt:", '"Summarize this email in 3 bullets: key points, action items, deadlines"'),
        ("Tool:", "Make.com")
    ]

    for label, value in examples:
        c.setFont("Helvetica-Bold", 9)
        c.drawString(90, y_position, label)
        c.setFont("Helvetica", 9)
        c.drawString(140, y_position, value)
        y_position -= 14

    # Footer with branding
    c.setFont("Helvetica-Oblique", 8)
    c.setFillColor(HexColor("#9CA3AF"))
    footer_text = "Your First AI Workflow Template - Start automating today!"
    c.drawCentredString(width / 2, 40, footer_text)

    # Save the PDF
    c.save()
    print(f"[SUCCESS] Interactive fillable PDF workbook created: {output_path}")

if __name__ == "__main__":
    output_path = r"C:\Users\sabaa\OneDrive\Desktop\TEST_AGENTS\MARKETING_TEAM\outputs\pdfs\prompt_to_process_template.pdf"

    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    create_fillable_workbook(output_path)
