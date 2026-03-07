
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
from reportlab.lib.units import inch
from datetime import datetime

def create_report(filename):
    doc = SimpleDocTemplate(filename, pagesize=A4, margin=72)
    styles = getSampleStyleSheet()
    
    # Custom Styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Title'],
        fontSize=24,
        spaceAfter=30,
        textColor=colors.HexColor('#1a237e')
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading1'],
        fontSize=18,
        spaceBefore=20,
        spaceAfter=12,
        textColor=colors.HexColor('#283593')
    )
    
    subheading_style = ParagraphStyle(
        'CustomSubHeading',
        parent=styles['Heading2'],
        fontSize=14,
        spaceBefore=15,
        spaceAfter=10,
        textColor=colors.HexColor('#303f9f')
    )
    
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontSize=11,
        leading=16,
        spaceAfter=10,
        alignment=4  # Justified
    )

    story = []

    # Title Page
    story.append(Spacer(1, 2*inch))
    story.append(Paragraph("FORENSIC CRIME SCENE RECONSTRUCTION SYSTEM", title_style))
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph(f"Project Implementation Report", heading_style))
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph(f"Date: {datetime.now().strftime('%B %d, %Y')}", body_style))
    story.append(Spacer(1, 3*inch))
    story.append(Paragraph("<b>Submitted by:</b> [Your Name]", body_style))
    story.append(Paragraph("<b>Department:</b> Computer Science & Engineering", body_style))
    story.append(PageBreak())

    # 1. Abstract
    story.append(Paragraph("1. Abstract", heading_style))
    abstract_text = """
    This project presents a state-of-the-art Forensic Crime Scene Reconstruction System designed to modernize crime scene investigation techniques. 
    By leveraging photogrammetry (Structure from Motion), the system converts standard 2D crime scene photographs into accurate, interactive 3D models. 
    It addresses critical challenges in forensic analysis, including spatial preservation, evidence integrity (Chain of Custody), and legal compliance 
    with the Bharatiya Sakshya Adhiniyam (BSA) and Indian Evidence Act. The system provides a unified platform for reconstruction, measurement, 
    analysis, and automated report generation.
    """
    story.append(Paragraph(abstract_text, body_style))

    # 2. Introduction
    story.append(Paragraph("2. Introduction", heading_style))
    intro_text = """
    Traditional crime scene documentation relies heavily on manual sketches and 2D photography, which can lack depth information and spatial context. 
    This project aims to bridge that gap by implementing a web-based solution that allows forensic examiners to upload images, reconstruct the scene in 3D, 
    and perform virtual measurements with high precision.
    """
    story.append(Paragraph(intro_text, body_style))

    # 3. Technologies Used
    story.append(Paragraph("3. Technologies Used", heading_style))
    story.append(Paragraph("The project is built using a modern, robust tech stack:", body_style))
    
    # Tech Table
    tech_data = [
        ['Component', 'Technology', 'Purpose'],
        ['Frontend', 'React.js + TypeScript', 'User Interface & Interaction'],
        ['UI Framework', 'Material UI (MUI)', 'Responsive Design'],
        ['3D Rendering', 'Three.js / React Three Fiber', 'Visualize 3D Models & Point Clouds'],
        ['Backend API', 'FastAPI (Python)', 'High-performance Asynchronous API'],
        ['Database', 'PostgreSQL / SQLite', 'Data Persistence & Audit Logging'],
        ['ORM', 'SQLAlchemy', 'Database Abstraction'],
        ['Photogrammetry', 'OpenCV + COLMAP', 'Structure from Motion (SfM) Pipeline'],
        ['Image Processing', 'Pillow / NumPy', 'Metadata Extraction & Analysis'],
        ['Reporting', 'ReportLab', 'PDF Generation'],
    ]
    
    t = Table(tech_data, colWidths=[1.5*inch, 2.5*inch, 2.5*inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e8eaf6')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#1a237e')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.lightgrey),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(t)

    # 4. System Architecture
    story.append(Paragraph("4. System Architecture", heading_style))
    arch_text = """
    The system follows a modular client-server architecture:
    """
    story.append(Paragraph(arch_text, body_style))
    
    architecture_steps = [
        "<b>Frontend Layer:</b> Captures user inputs, handles image uploads, and renders the 3D viewer using WebGL technology. It communicates with the backend via RESTful APIs.",
        "<b>Backend Layer:</b> The core logic engine. It handles authentication, data validation, and orchestrates the heavy-lifting of image processing and photogrammetry tasks.",
        "<b>Data Storage Layer:</b> Manages persistent data, including case files, evidence images, generated 3D assets, and the immutable Chain of Custody logs."
    ]
    
    for step in architecture_steps:
        story.append(Paragraph(f"• {step}", body_style))

    # 5. Implementation Details
    story.append(Paragraph("5. Implementation Details", heading_style))
    
    story.append(Paragraph("5.1 Image Processing & Photogrammetry", subheading_style))
    sfm_text = """
    The heart of the system is the Structure from Motion (SfM) pipeline. 
    1. Feature Extraction: SIFT features are detected in uploaded images.
    2. Feature Matching: Matches are found between image pairs.
    3. Sparse Reconstruction: Camera poses and 3D points are estimated.
    4. Dense Reconstruction: Depth maps are generated to create a dense point cloud.
    """
    story.append(Paragraph(sfm_text, body_style))

    story.append(Paragraph("5.2 Chain of Custody (CoC)", subheading_style))
    coc_text = """
    To ensure legal admissibility, every action is logged. When images are uploaded, their SHA-256 hash is calculated immediately. 
    Any future access or modification is cross-referenced against this hash to detect tampering.
    """
    story.append(Paragraph(coc_text, body_style))

    story.append(Paragraph("5.3 3D Visualization", subheading_style))
    viz_text = """
    The frontend utilizes React Three Fiber to load and display .PLY and .OBJ files. 
    Users can rotate, pan, and zoom into the crime scene. A custom measurement tool allows users to click two points in 3D space to calculate real-world distances.
    """
    story.append(Paragraph(viz_text, body_style))
    
    # 6. Database Design
    story.append(Paragraph("6. Database Design", heading_style))
    db_text = """
    The application uses a relational database model with the following key entities:
    """
    story.append(Paragraph(db_text, body_style))
    db_points = [
        "<b>Projects:</b> Stores case metadata (e.g., location, examiner).",
        "<b>Images:</b> Stores file paths, hashes, and EXIF data.",
        "<b>Reconstructions:</b> Links to generated 3D model files.",
        "<b>Measurements:</b> Stores user-generated analysis data."
    ]
    for p in db_points:
        story.append(Paragraph(f"• {p}", body_style))

    # 7. Conclusion
    story.append(Paragraph("7. Conclusion", heading_style))
    concl_text = """
    This project successfully demonstrates the application of modern computer vision techniques in forensic science. 
    By creating an accessible, accurate, and compliant tool, it empowers forensic examiners to document logic scenes more effectively than ever before.
    """
    story.append(Paragraph(concl_text, body_style))

    doc.build(story)
    print(f"PDF Report generated successfully: {filename}")

if __name__ == "__main__":
    create_report("Project_Creation_Report.pdf")
