from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
import os

# Define brand colors
precision_gold = colors.HexColor('#B8860B')
tactical_cyan = colors.HexColor('#4A90A4')
void_black = colors.HexColor('#0A0E14')

# Paths
output_path = r'C:\Users\sabaa\OneDrive\Desktop\TEST_AGENTS\MARKETING_TEAM\outputs\pdfs\Dux_Machina_Capability_Statement_Final.pdf'
logo_path = r'C:\Users\sabaa\Downloads\DMOS_LOGO.png'

# Create output directory if needed
os.makedirs(os.path.dirname(output_path), exist_ok=True)

# Create PDF
doc = SimpleDocTemplate(output_path, pagesize=letter,
                       topMargin=0.5*inch, bottomMargin=0.5*inch,
                       leftMargin=0.6*inch, rightMargin=0.6*inch)

# Styles
styles = getSampleStyleSheet()

title_style = ParagraphStyle(
    'CustomTitle',
    parent=styles['Heading1'],
    fontSize=28,
    textColor=precision_gold,
    spaceAfter=6,
    alignment=TA_CENTER,
    fontName='Helvetica-Bold'
)

tagline_style = ParagraphStyle(
    'Tagline',
    parent=styles['Normal'],
    fontSize=12,
    textColor=tactical_cyan,
    spaceAfter=4,
    alignment=TA_CENTER,
    fontName='Helvetica-Bold'
)

subtitle_style = ParagraphStyle(
    'Subtitle',
    parent=styles['Normal'],
    fontSize=9,
    textColor=void_black,
    spaceAfter=12,
    alignment=TA_CENTER,
    fontName='Helvetica'
)

section_header = ParagraphStyle(
    'SectionHeader',
    parent=styles['Heading2'],
    fontSize=12,
    textColor=colors.white,
    spaceAfter=8,
    spaceBefore=10,
    alignment=TA_LEFT,
    fontName='Helvetica-Bold',
    backColor=tactical_cyan,
    leftIndent=8,
    rightIndent=8,
    borderPadding=6
)

body_style = ParagraphStyle(
    'CustomBody',
    parent=styles['Normal'],
    fontSize=9,
    textColor=void_black,
    spaceAfter=8,
    alignment=TA_JUSTIFY,
    fontName='Helvetica',
    leading=11
)

bullet_style = ParagraphStyle(
    'BulletStyle',
    parent=styles['Normal'],
    fontSize=8.5,
    textColor=void_black,
    spaceAfter=3,
    alignment=TA_LEFT,
    fontName='Helvetica',
    leftIndent=12,
    bulletIndent=6,
    leading=10
)

diff_title_style = ParagraphStyle(
    'DiffTitle',
    parent=styles['Normal'],
    fontSize=9,
    textColor=precision_gold,
    spaceAfter=3,
    alignment=TA_LEFT,
    fontName='Helvetica-Bold',
    leading=11
)

diff_body_style = ParagraphStyle(
    'DiffBody',
    parent=styles['Normal'],
    fontSize=8.5,
    textColor=void_black,
    spaceAfter=6,
    alignment=TA_JUSTIFY,
    fontName='Helvetica',
    leading=10
)

contact_style = ParagraphStyle(
    'Contact',
    parent=styles['Normal'],
    fontSize=8,
    textColor=void_black,
    spaceAfter=2,
    alignment=TA_LEFT,
    fontName='Helvetica'
)

footer_style = ParagraphStyle(
    'Footer',
    parent=styles['Normal'],
    fontSize=7,
    textColor=colors.grey,
    alignment=TA_CENTER,
    fontName='Helvetica'
)

# Build content
story = []

# Logo and Header
logo = Image(logo_path, width=1.2*inch, height=1.2*inch)
logo.hAlign = 'CENTER'
story.append(logo)

story.append(Paragraph('DUX MACHINA OS', title_style))
story.append(Paragraph('Strategy that builds. Systems that scale.', tagline_style))
story.append(Paragraph('AI-Native Systems Consulting &amp; Integration', subtitle_style))
story.append(Spacer(1, 0.15*inch))

# Company Overview
story.append(Paragraph('COMPANY OVERVIEW', section_header))
overview_text = 'DUX MACHINA OS is an AI-native systems consulting and integration firm specializing in cloud architecture, cybersecurity, automation, and intelligent infrastructure for federal and enterprise clients. We design and implement mission-critical systems that unify operations, data, and decision-making across complex environments. Our multidisciplinary team combines expertise in AI, cloud, security, and DevSecOps to deliver resilient, compliant, and scalable solutions aligned with federal modernization goals.'
story.append(Paragraph(overview_text, body_style))
story.append(Spacer(1, 0.1*inch))

# Mission Statement
story.append(Paragraph('MISSION STATEMENT', section_header))
mission_text = 'Our mission is to empower government and enterprise organizations with secure, AI-enabled infrastructure that enhances operational efficiency, strengthens cybersecurity posture, and supports data-driven decision-making across all mission domains. We serve as both an advisor and implementation partner—bridging strategy, architecture, and execution to deliver measurable transformation.'
story.append(Paragraph(mission_text, body_style))
story.append(Spacer(1, 0.1*inch))

# Core Competencies
story.append(Paragraph('CORE COMPETENCIES', section_header))

competencies = [
    ['• Cloud Architecture &amp; Deployment', '• Infrastructure as Code (Terraform, Ansible)', '• Database &amp; API Management'],
    ['• System Architecture &amp; Design', '• CI/CD Pipeline Automation', '• System Reliability Engineering (SRE)'],
    ['• Security Architecture &amp; Compliance', '• DevSecOps Implementation', '• Program &amp; Project Management'],
    ['• Data Architecture &amp; Integration', '• Containerization &amp; Orchestration (Docker, Kubernetes, ECS)', '• Documentation &amp; Technical Writing'],
    ['• AI/ML Engineering &amp; Model Deployment', '• Continuous Monitoring &amp; Incident Response', '• Legacy Application Migration'],
    ['', '• Vulnerability Assessment &amp; Risk Mitigation', '• End User Training'],
    ['', '• Quality Assurance &amp; Automation Testing', '']
]

comp_table_data = []
for row in competencies:
    comp_table_data.append([Paragraph(cell, bullet_style) if cell else '' for cell in row])

comp_table = Table(comp_table_data, colWidths=[2.3*inch, 2.3*inch, 2.3*inch])
comp_table.setStyle(TableStyle([
    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ('LEFTPADDING', (0, 0), (-1, -1), 3),
    ('RIGHTPADDING', (0, 0), (-1, -1), 3),
    ('TOPPADDING', (0, 0), (-1, -1), 2),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
]))

story.append(comp_table)
story.append(Spacer(1, 0.1*inch))

# Differentiators
story.append(Paragraph('DIFFERENTIATORS', section_header))

differentiators = [
    ('1. AI-Native Architecture Consulting:', 'Adaptive systems built with intelligence at the core, not bolted on.'),
    ('2. Zero Trust + DevSecOps Integration:', 'Security embedded from design to deployment across the lifecycle.'),
    ('3. Full Lifecycle Modernization:', 'From legacy migration to continuous optimization and managed services.'),
    ('4. Proven Federal Experience:', 'Architectural leadership and modernization support across USPS, USDA, and other federal programs.'),
    ('5. Compliance Readiness:', 'Demonstrated alignment with FedRAMP, NIST 800-53, NIST 800-171, SOC 2, ISO 27001, HIPAA, PCI-DSS, and FISMA frameworks to support secure, scalable federal and commercial deployments.'),
    ('6. Cross-Domain Expertise:', 'Integration of AI, Cloud, Security, and Data into one unified operating framework.')
]

for title, desc in differentiators:
    story.append(Paragraph(title, diff_title_style))
    story.append(Paragraph(desc, diff_body_style))

story.append(Spacer(1, 0.1*inch))

# Compliance Frameworks
story.append(Paragraph('COMPLIANCE FRAMEWORKS', section_header))
compliance_text = '<b>FedRAMP</b> | <b>NIST 800-53</b> | <b>NIST 800-171</b> | <b>SOC 2</b> | <b>ISO 27001</b> | <b>HIPAA</b> | <b>PCI-DSS</b> | <b>FISMA</b>'
compliance_para = ParagraphStyle('Compliance', parent=body_style, alignment=TA_CENTER, fontSize=8.5, textColor=tactical_cyan, fontName='Helvetica-Bold')
story.append(Paragraph(compliance_text, compliance_para))
story.append(Spacer(1, 0.15*inch))

# Contact Information
story.append(Paragraph('CONTACT INFORMATION', section_header))
contact_data = [
    [Paragraph('<b>Email:</b> info@duxmachina.com', contact_style), Paragraph('<b>Phone:</b> (301) 448-9941', contact_style)],
    [Paragraph('<b>Location:</b> Washington, D.C. Metro', contact_style), Paragraph('<b>Website:</b> https://duxmachina.com', contact_style)]
]

contact_table = Table(contact_data, colWidths=[3.5*inch, 3.5*inch])
contact_table.setStyle(TableStyle([
    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ('LEFTPADDING', (0, 0), (-1, -1), 6),
    ('RIGHTPADDING', (0, 0), (-1, -1), 6),
]))

story.append(contact_table)
story.append(Spacer(1, 0.2*inch))

# Footer
story.append(Paragraph('© 2025 DUX MACHINA OS. All rights reserved.', footer_style))

# Build PDF
doc.build(story)

print(f'PDF created successfully: {output_path}')
