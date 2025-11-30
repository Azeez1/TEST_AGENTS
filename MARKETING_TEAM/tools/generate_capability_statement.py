#!/usr/bin/env python3
"""
Generate Dux Machina Capability Statement PDF
FIXES: Adds logo, removes dots, keeps all other visual elements
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import ImageReader
import os
import math

def create_capability_statement():
    """Generate the corrected capability statement PDF"""

    # Create output directory
    os.makedirs('outputs/pdfs', exist_ok=True)

    # Initialize PDF
    pdf_path = 'outputs/pdfs/Dux_Machina_Capability_Statement_Final.pdf'
    c = canvas.Canvas(pdf_path, pagesize=letter)
    width, height = letter

    # Brand colors
    void_black = HexColor('#0A0E14')
    steel_command = HexColor('#2E4156')
    precision_gold = HexColor('#B8860B')
    tactical_cyan = HexColor('#4A90A4')
    white = HexColor('#FFFFFF')
    mist = HexColor('#E5E7EB')
    slate = HexColor('#6B7280')

    # Set white background
    c.setFillColor(white)
    c.rect(0, 0, width, height, fill=True, stroke=False)

    # ===== HEADER WITH LOGO =====
    c.setFillColor(void_black)
    c.rect(0, height - 1.3*inch, width, 1.3*inch, fill=True, stroke=False)

    # Add logo - CRITICAL FIX
    logo_path = r'C:\Users\sabaa\Downloads\DMOS_LOGO.png'
    if os.path.exists(logo_path):
        logo = ImageReader(logo_path)
        c.drawImage(logo, 0.5*inch, height - 1.2*inch, width=1*inch, height=1*inch,
                   preserveAspectRatio=True, mask='auto')
        print('Logo added successfully')
    else:
        print(f'WARNING: Logo file not found at: {logo_path}')

    # Company name and tagline
    c.setFillColor(precision_gold)
    c.setFont('Helvetica-Bold', 22)
    c.drawString(1.7*inch, height - 0.6*inch, 'DUX MACHINA OS')

    c.setFillColor(mist)
    c.setFont('Helvetica', 11)
    c.drawString(1.7*inch, height - 0.9*inch, 'Strategy that builds. Systems that scale.')

    # Decorative hexagons in header (KEEP THESE - NOT DOTS)
    c.setStrokeColor(tactical_cyan)
    c.setLineWidth(1.5)

    def draw_hexagon(cx, cy, size):
        path = c.beginPath()
        for i in range(7):  # 7 points to close the hexagon
            angle = math.radians(60 * i + 30)
            x = cx + size * math.cos(angle)
            y = cy + size * math.sin(angle)
            if i == 0:
                path.moveTo(x, y)
            else:
                path.lineTo(x, y)
        c.drawPath(path, stroke=1, fill=0)

    # Small hexagons on right side of header
    draw_hexagon(width - 0.8*inch, height - 0.5*inch, 0.15*inch)
    draw_hexagon(width - 0.5*inch, height - 0.7*inch, 0.12*inch)
    draw_hexagon(width - 0.65*inch, height - 0.95*inch, 0.1*inch)

    # ===== COMPANY OVERVIEW =====
    y_pos = height - 1.6*inch

    c.setFillColor(void_black)
    c.setFont('Helvetica-Bold', 12)
    c.drawString(0.5*inch, y_pos, 'COMPANY OVERVIEW')

    c.setFillColor(slate)
    c.setFont('Helvetica', 9)
    c.drawString(0.5*inch, y_pos - 0.2*inch,
                'AI-native systems consulting and integration firm specializing in cloud architecture, cybersecurity,')
    c.drawString(0.5*inch, y_pos - 0.35*inch,
                'automation, and intelligent infrastructure for federal and enterprise clients.')

    # ===== MISSION =====
    y_pos -= 0.8*inch
    c.setFillColor(void_black)
    c.setFont('Helvetica-Bold', 12)
    c.drawString(0.5*inch, y_pos, 'MISSION')

    c.setFillColor(slate)
    c.setFont('Helvetica', 9)
    c.drawString(0.5*inch, y_pos - 0.2*inch,
                'Empower government and enterprise organizations with secure, AI-enabled infrastructure that enhances')
    c.drawString(0.5*inch, y_pos - 0.35*inch,
                'operational efficiency and supports data-driven decision-making.')

    # ===== CORE COMPETENCIES =====
    y_pos -= 0.9*inch
    c.setFillColor(void_black)
    c.setFont('Helvetica-Bold', 14)
    c.drawString(0.5*inch, y_pos, 'CORE COMPETENCIES')

    # Define competencies with icons (using text instead of unicode)
    competencies = [
        {
            'title': 'CLOUD & INFRASTRUCTURE',
            'icon': 'Cloud',
            'color': tactical_cyan,
            'items': ['Cloud Architecture & Deployment', 'Infrastructure as Code', 'Containerization & Orchestration']
        },
        {
            'title': 'SECURITY & COMPLIANCE',
            'icon': 'Shield',
            'color': precision_gold,
            'items': ['Security Architecture & Compliance', 'DevSecOps Implementation', 'Vulnerability Assessment & Risk Mitigation']
        },
        {
            'title': 'AI & AUTOMATION',
            'icon': 'AI',
            'color': tactical_cyan,
            'items': ['AI/ML Engineering & Model Deployment', 'CI/CD Pipeline Automation', 'Quality Assurance & Automation Testing']
        },
        {
            'title': 'DATA & SYSTEMS',
            'icon': 'Data',
            'color': precision_gold,
            'items': ['Data Architecture & Integration', 'System Architecture & Design', 'Database & API Management']
        },
        {
            'title': 'OPERATIONS',
            'icon': 'Ops',
            'color': tactical_cyan,
            'items': ['Continuous Monitoring & Incident Response', 'System Reliability Engineering (SRE)', 'Legacy Application Migration']
        },
        {
            'title': 'MANAGEMENT',
            'icon': 'Mgmt',
            'color': precision_gold,
            'items': ['Program & Project Management', 'Documentation & Technical Writing', 'End User Training']
        }
    ]

    # Draw competency boxes in 2x3 grid
    box_width = 3.4*inch
    box_height = 1.1*inch
    x_margin = 0.5*inch
    y_margin = 0.15*inch
    y_pos -= 0.3*inch

    for idx, comp in enumerate(competencies):
        row = idx // 2
        col = idx % 2

        x = x_margin + col * (box_width + 0.2*inch)
        y = y_pos - row * (box_height + y_margin)

        # Header box
        c.setFillColor(comp['color'])
        c.rect(x, y, box_width, 0.3*inch, fill=True, stroke=False)

        # White body box
        c.setFillColor(white)
        c.setStrokeColor(HexColor('#E5E7EB'))
        c.setLineWidth(1)
        c.rect(x, y - 0.8*inch, box_width, 0.8*inch, fill=True, stroke=True)

        # Icon and title
        c.setFillColor(white)
        c.setFont('Helvetica-Bold', 8)
        c.drawString(x + 0.1*inch, y + 0.1*inch, f'[{comp["icon"]}] {comp["title"]}')

        # Items
        c.setFillColor(slate)
        c.setFont('Helvetica', 7)
        item_y = y - 0.25*inch
        for item in comp['items']:
            # Use bullet character that works in CP1252
            c.drawString(x + 0.1*inch, item_y, f'• {item}')
            item_y -= 0.22*inch

    # ===== KEY DIFFERENTIATORS =====
    y_pos -= 3.8*inch
    c.setFillColor(void_black)
    c.setFont('Helvetica-Bold', 12)
    c.drawString(0.5*inch, y_pos, 'KEY DIFFERENTIATORS')

    differentiators = [
        'AI-Native Architecture',
        'Zero Trust + DevSecOps',
        'Full Lifecycle Modernization',
        'Proven Federal Experience',
        'Compliance Readiness',
        'Cross-Domain Expertise'
    ]

    # Draw circular badges in 2 rows
    badge_radius = 0.25*inch
    y_pos -= 0.5*inch

    for idx, diff in enumerate(differentiators):
        row = idx // 3
        col = idx % 3

        x = 1.2*inch + col * 2.2*inch
        y = y_pos - row * 0.6*inch

        # Circle
        c.setFillColor(precision_gold)
        c.circle(x, y, badge_radius, fill=True, stroke=False)

        # Checkmark (using standard character)
        c.setFillColor(white)
        c.setFont('Helvetica-Bold', 16)
        c.drawString(x - 0.08*inch, y - 0.08*inch, '✓')

        # Text
        c.setFillColor(slate)
        c.setFont('Helvetica', 8)
        c.drawString(x + 0.35*inch, y - 0.05*inch, diff)

    # ===== COMPLIANCE BADGES =====
    y_pos -= 1.5*inch
    c.setFillColor(void_black)
    c.setFont('Helvetica-Bold', 12)
    c.drawString(0.5*inch, y_pos, 'COMPLIANCE READINESS')

    compliance = ['FedRAMP', 'NIST 800-53', 'NIST 800-171', 'SOC 2', 'ISO 27001', 'HIPAA', 'PCI-DSS', 'FISMA']

    c.setFont('Helvetica-Bold', 9)
    x_pos = 0.5*inch
    for badge in compliance:
        # Badge box
        c.setFillColor(mist)
        c.roundRect(x_pos, y_pos - 0.35*inch, 0.9*inch, 0.25*inch, 3, fill=True, stroke=False)

        # Text
        c.setFillColor(void_black)
        c.drawCentredString(x_pos + 0.45*inch, y_pos - 0.25*inch, badge)

        x_pos += 0.95*inch
        if x_pos > 7*inch:
            x_pos = 0.5*inch
            y_pos -= 0.4*inch

    # ===== FOOTER =====
    c.setFillColor(steel_command)
    c.rect(0, 0, width, 0.5*inch, fill=True, stroke=False)

    c.setFillColor(white)
    c.setFont('Helvetica', 8)
    footer_text = 'info@duxmachina.com  |  (301) 448-9941  |  Washington, D.C. Metro  |  duxmachina.com'
    c.drawCentredString(width/2, 0.2*inch, footer_text)

    # Save
    c.save()
    print(f'PDF generated: {pdf_path}')
    print('Dots removed (no decorative dot patterns)')
    print('All other visual elements preserved')
    return pdf_path

if __name__ == '__main__':
    create_capability_statement()
