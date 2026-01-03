"""
Utility module for generating offer letter PDFs with company branding - Exact Template Match
"""
import os
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_JUSTIFY, TA_LEFT
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib import colors
from django.conf import settings


def generate_offer_letter_pdf(data):
    """
    Generate offer letter PDF from form data with exact company template formatting
    
    Args:
        data: Dictionary containing offer letter information
        
    Returns:
        BytesIO buffer containing the PDF
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                            rightMargin=72, leftMargin=72,
                            topMargin=20, bottomMargin=20)
    
    # Container for the 'Flowable' objects
    elements = []
    styles = getSampleStyleSheet()
    
    # Get base directory for images
    base_dir = settings.BASE_DIR
    header_path = os.path.join(base_dir, 'header.png')
    footer_path = os.path.join(base_dir, 'foter.png')
    sign_path = os.path.join(base_dir, 'sign.png')
    location_icon_path = os.path.join(base_dir, 'image_above_left.png')
    
    # Add header image if exists
    if os.path.exists(header_path):
        try:
            # Header with logo and colorful design
            header_img = Image(header_path, width=6.5*inch, height=0.6*inch)
            elements.append(header_img)
            elements.append(Spacer(1, 6))
        except Exception as e:
            print(f"Could not load header image: {e}")
            pass
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=colors.HexColor('#000000'),
        spaceAfter=20,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=11,
        leading=16,
        alignment=TA_JUSTIFY,
        spaceAfter=12
    )
    
    left_style = ParagraphStyle(
        'LeftAlign',
        parent=styles['Normal'],
        fontSize=10,
        alignment=TA_LEFT
    )
    
    right_style = ParagraphStyle(
        'RightAlign',
        parent=styles['Normal'],
        fontSize=10,
        alignment=TA_RIGHT
    )
    
    # Reference number and date (underlined)
    ref_text = f'<u><b>{data["reference_number"]}</b></u>'
    date_text = f'<u>-- /{data["offer_date"]}</u>'
    
    ref_table = Table([[Paragraph(ref_text, left_style), Paragraph(date_text, right_style)]], 
                      colWidths=[3.5*inch, 3*inch])
    elements.append(ref_table)
    elements.append(Spacer(1, 24))
    
    # Candidate name (underlined)
    elements.append(Paragraph(f'<u>Mr. {data["candidate_name"]}</u>', left_style))
    elements.append(Spacer(1, 36))
    
    # Title
    elements.append(Paragraph('<b><u>Offer Letter</u></b>', title_style))
    elements.append(Spacer(1, 12))
    
    # Greeting (Bold)
    elements.append(Paragraph(f'<b>Dear. {data["candidate_name"].split()[0]},</b>', normal_style))
    elements.append(Spacer(1, 12))
    
    # Main content paragraph 1 with underlines
    para1 = f'''This is Reference to your application and Subsequent interviews you had with us. We are pleased to offer you the position of <u><b>{data["designation_display"]}</b></u> in <u><b>{data["department"]}</b></u> with effect from <u><b>{data["joining_date"]}</b></u>, on the terms and conditions as mutually agreed upon at the time of interview.'''
    elements.append(Paragraph(para1, normal_style))
    elements.append(Spacer(1, 12))
    
    # Team details if provided
    if data.get('team_details'):
        para2 = f'<b>As per discussion:</b>- {data["team_details"]}'
        elements.append(Paragraph(para2, normal_style))
        elements.append(Spacer(1, 12))
    
    # Salary information (underlined and bold)
    salary_para = f'''As discussed, your annual Income would be Rupees <u><b>{data["annual_salary"]}/- ({data["salary_in_words"]})</b></u>'''
    elements.append(Paragraph(salary_para, normal_style))
    elements.append(Spacer(1, 24))
    
    # Probation period
    probation_para = '''You will be on probation for a period of six months at the end of which provided your performance has been found satisfactory you may be confirmed as an employee in the company.'''
    elements.append(Paragraph(probation_para, normal_style))
    
    # Confidentiality (with underlines)
    conf_para = '''You <u>will be required to enter into a Confidentiality Agreement with the Company and provide the accurate</u> information to <u>be filled in</u> your joining form, sending along with your offer letter.'''
    elements.append(Paragraph(conf_para, normal_style))
    elements.append(Spacer(1, 12))
    
    # Acceptance instructions with underlined email
    accept_para = f'''Please sign a duplicate copy of this letter and fill the joining form as a token of your acceptance and send the same email id <u><b>hr_shilpisaxena@eomshopping.in</b></u> (HR Team) <u>back</u> to us. The offer letter and joining kit <u>will</u> valid for 2 days only from the day the <u>it</u> is issued.'''
    elements.append(Paragraph(accept_para, normal_style))
    elements.append(Spacer(1, 12))
    
    # Welcome message
    welcome_para = '''We Welcome you and look forward for your arrival in <b>EASY ONLINE MARKETING</b>.'''
    elements.append(Paragraph(welcome_para, normal_style))
    elements.append(Paragraph('Thanking You Sincerely', normal_style))
    elements.append(Spacer(1, 12))
    
    # Signature section
    sig_elements = []
    
    # Left side - Company signature with stamp
    left_content = [
        [Paragraph('For <b>EASY ONLINE MARKETING</b>', left_style)],
        [Spacer(1, 6)],
    ]
    
    # Add signature stamp if exists
    if os.path.exists(sign_path):
        try:
            sign_img = Image(sign_path, width=1.5*inch, height=1.5*inch)
            left_content.append([sign_img])
        except:
            left_content.append([Spacer(1, 40)])
    else:
        left_content.append([Spacer(1, 40)])
    
    left_content.append([Paragraph('<b>Authorized Signatory</b>', left_style)])
    
    # Right side - Applicant signature
    right_style_center = ParagraphStyle(
        'RightCenter',
        parent=styles['Normal'],
        fontSize=10,
        alignment=TA_CENTER
    )
    
    right_content = [
        [Paragraph('I accept the terms and conditions', right_style_center)],
        [Spacer(1, 60)],
        [Paragraph('<u><b>Name(Change)</b></u>', right_style_center)],
        [Paragraph('<b>Signature of Applicant</b>', right_style_center)],
    ]
    
    # Create tables for left and right
    left_table = Table(left_content, colWidths=[2.5*inch])
    left_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
    ]))
    
    right_table = Table(right_content, colWidths=[2.5*inch])
    right_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ]))
    
    # Combine left and right in one table
    sig_table = Table([[left_table, '', right_table]], colWidths=[2.5*inch, 1*inch, 2.5*inch])
    sig_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    
    elements.append(sig_table)
    elements.append(Spacer(1, 24))
    
    # Add footer image if exists
    if os.path.exists(footer_path):
        try:
            footer_img = Image(footer_path, width=6.5*inch, height=0.8*inch)
            elements.append(footer_img)
        except:
            # Fallback: Add location icon and address text
            footer_elements = []
            
            # Location icon if exists
            if os.path.exists(location_icon_path):
                try:
                    location_img = Image(location_icon_path, width=0.3*inch, height=0.3*inch)
                    footer_elements.append(location_img)
                    footer_elements.append(Spacer(1, 6))
                except:
                    pass
            
            # Address text
            footer_text = '''8119, 8th Floor, Gaur City Office Mall, Sector – 4 Greater Noida West, Gautam Buddha Nagar Uttar Pradesh – 201306, India'''
            footer_style = ParagraphStyle(
                'Footer',
                parent=styles['Normal'],
                fontSize=9,
                alignment=TA_CENTER,
                textColor=colors.HexColor('#666666')
            )
            footer_elements.append(Paragraph(footer_text, footer_style))
            
            for elem in footer_elements:
                elements.append(elem)
    
    # Build PDF
    doc.build(elements)
    
    # Get the value of the BytesIO buffer and return it
    pdf = buffer.getvalue()
    buffer.close()
    return pdf
