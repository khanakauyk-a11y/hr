"""
Utility module for generating appointment letter PDFs with company branding - Updated Format
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
    Generate appointment letter PDF from form data with company template formatting
    
    Args:
        data: Dictionary containing appointment letter information
        
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
    
    # Add header image if exists
    if os.path.exists(header_path):
        try:
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
    
    bold_style = ParagraphStyle(
        'BoldStyle',
        parent=normal_style,
        fontName='Helvetica-Bold'
    )
    
    # Reference number and date
    ref_text = f'<b>{data["reference_number"]}</b>'
    date_text = f'{data["offer_date"]}'
    
    ref_table = Table([[Paragraph(ref_text, left_style), Paragraph(date_text, right_style)]], 
                      colWidths=[3.5*inch, 3*inch])
    elements.append(ref_table)
    elements.append(Spacer(1, 24))
    
    # Candidate name
    elements.append(Paragraph(f'Ms. {data["candidate_name"]}', left_style))
    elements.append(Spacer(1, 36))
    
    # Title - APPOINTMENT LETTER
    elements.append(Paragraph('<b><u>APPOINTMENT LETTER</u></b>', title_style))
    elements.append(Spacer(1, 12))
    
    # Greeting
    elements.append(Paragraph(f'Dear Ms. {data["candidate_name"].split()[0]},', normal_style))
    elements.append(Spacer(1, 12))
    
    # Main content paragraph
    para1 = f'''This is with reference to your application and the subsequent discussions you had with us. We are pleased to appointment you the position of <b>{data["designation_display"]} – Department Retainer Sales & Marketing</b>, effective <b>{data["joining_date"]}</b>, on the terms and conditions mutually agreed upon during the interview process.'''
    elements.append(Paragraph(para1, normal_style))
    elements.append(Spacer(1, 12))
    
    # Salary information
    salary_para = f'''As discussed, your annual Amount would be Rupees <b>{data["annual_salary"]}/- ({data["salary_in_words"]})</b>'''
    elements.append(Paragraph(salary_para, normal_style))
    elements.append(Spacer(1, 12))
    
    # Role & Responsibilities section
    elements.append(Paragraph('<b><u>Role & Responsibilities:</u></b>', bold_style))
    elements.append(Spacer(1, 6))
    
    role_para = '''In this role, you will be responsible for recruiting direct reportees and supporting structured team expansion through effective leadership. Over a period of time, you will be expected to manage and supervise a team strength of 40–50 members.'''
    elements.append(Paragraph(role_para, normal_style))
    elements.append(Spacer(1, 12))
    
    # Performance Expectations section
    elements.append(Paragraph('<b><u>Performance Expectations:</u></b>', bold_style))
    elements.append(Spacer(1, 6))
    
    perf_intro = 'As discussed, during the initial phase you will be expected to:'
    elements.append(Paragraph(perf_intro, normal_style))
    
    # Bullet points for performance expectations
    bullet_style = ParagraphStyle(
        'Bullet',
        parent=normal_style,
        leftIndent=20,
        bulletIndent=10
    )
    
    perf_points = [
        'Recruit a minimum of 3 candidates as per business requirements (positions will be communicated from time to time).',
        'Close at least 1 sale within the first 2 working days of joining.',
        'Achieve a minimum of 4 sales per month, which will remain mandatory until the team reaches its planned strength.'
    ]
    
    for point in perf_points:
        elements.append(Paragraph(f'• {point}', bullet_style))
    
    elements.append(Spacer(1, 12))
    
    # Leave/Holidays section
    elements.append(Paragraph('<b>Leave/Holidays</b>', bold_style))
    elements.append(Spacer(1, 6))
    
    leave_points = [
        'You are entitled to no casual leave of day.',
        'You are entitled to working days of no paid sick leave.',
        'The Company will inform you in advance about the list of each declared holiday.'
    ]
    
    for point in leave_points:
        elements.append(Paragraph(f'• {point}', bullet_style))
    
    elements.append(Spacer(1, 24))
    
    # Department and probation paragraph
    dept_para = '''The department concerned shall be known as Retainer Sales & Marketing and all individuals joining this department shall be bound to comply with all departmental terms and conditions. You shall be on a probationary period of six (6) months, upon completion of which, subject to your performance being found satisfactory, you may, at the sole discretion of the Company, be confirmed as an employee or a permanent employee.'''
    elements.append(Paragraph(dept_para, normal_style))
    elements.append(Spacer(1, 12))
    
    # Confidentiality paragraph
    conf_para = '''You will be required to enter into a Confidentiality Agreement with the Company and provide accurate information to be filled in your joining form, sending along with your appointment letter.'''
    elements.append(Paragraph(conf_para, normal_style))
    elements.append(Spacer(1, 12))
    
    # Joining kit submission paragraph
    submit_para = '''All applicable terms and conditions are detailed in the joining kit. Submission of the duly filled joining kit along with the signed appointment letter shall be mandatory, and only upon receipt of both shall the appointment be deemed to have been accepted.'''
    elements.append(Paragraph(submit_para, normal_style))
    elements.append(Spacer(1, 12))
    
    # Acceptance instructions
    accept_para = f'''Please <b>sign</b> a duplicate copy of this letter and fill the joining form as a token of your acceptance and send the same email id <u><b>hr_vanshika@eomshopping.in</b></u> (HR Manager) back to us. The letter and joining kit will be valid for 2 days only from the day it is issued.'''
    elements.append(Paragraph(accept_para, normal_style))
    elements.append(Spacer(1, 12))
    
    # Welcome message
    welcome_para = '''We Welcome you and look forward for your arrival in EASY ONLINE MARKETING.'''
    elements.append(Paragraph(welcome_para, normal_style))
    elements.append(Paragraph('Thanking You Sincerely', normal_style))
    elements.append(Spacer(1, 12))
    
    # Signature section
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
        [Paragraph('<b>Sample</b>', right_style_center)],
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
            # Fallback footer
            footer_text = '''+91116926170 | info@eomshopping.in | info2@eomshopping.com<br/>
            8119, 8th Floor, Gaur City Office Mall, Sector – 4 Greater Noida West, Gautam Buddha Nagar Uttar Pradesh – 201306, India'''
            footer_style = ParagraphStyle(
                'Footer',
                parent=styles['Normal'],
                fontSize=9,
                alignment=TA_CENTER,
                textColor=colors.HexColor('#666666')
            )
            elements.append(Paragraph(footer_text, footer_style))
    
    # Build PDF
    doc.build(elements)
    
    # Get the value of the BytesIO buffer and return it
    pdf = buffer.getvalue()
    buffer.close()
    return pdf
