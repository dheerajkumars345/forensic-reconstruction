"""
Report Generation Service
Generates forensic PDF reports compliant with Bharatiya Sakshya Adhiniyam, 2023
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image as RLImage
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
import logging

from config import settings
from services.chain_of_custody import ChainOfCustodyService

logger = logging.getLogger(__name__)


class ReportGenerator:
    """Generate forensic PDF reports"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#1a237e'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        self.styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#283593'),
            spaceAfter=12,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        ))
        
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['BodyText'],
            fontSize=10,
            alignment=TA_JUSTIFY,
            spaceAfter=12
        ))
    
    def generate_forensic_report(
        self,
        output_path: Path,
        project_data: Dict[str, Any],
        images_data: List[Dict[str, Any]],
        reconstruction_data: Optional[Dict[str, Any]],
        measurements_data: List[Dict[str, Any]],
        audit_logs: List[Dict[str, Any]],
        include_images: bool = True,
        include_3d_views: bool = True,
        include_measurements: bool = True,
        include_audit_trail: bool = True,
        examiner_signature: Optional[str] = None,
        additional_notes: Optional[str] = None
    ) -> Path:
        """
        Generate comprehensive forensic report
        
        Args:
            output_path: Output PDF file path
            project_data: Project/case information
            images_data: List of image metadata
            reconstruction_data: 3D reconstruction information
            measurements_data: List of measurements
            audit_logs: Chain of custody logs
            include_images: Include image gallery
            include_3d_views: Include 3D model screenshots
            include_measurements: Include measurements table
            include_audit_trail: Include audit log
            examiner_signature: Examiner signature (if digitally signed)
            additional_notes: Additional notes or observations
            
        Returns:
            Path to generated PDF
        """
        try:
            logger.info(f"Generating forensic report: {output_path}")
            
            # Create PDF document
            doc = SimpleDocTemplate(
                str(output_path),
                pagesize=A4,
                rightMargin=2*cm,
                leftMargin=2*cm,
                topMargin=2*cm,
                bottomMargin=2*cm
            )
            
            # Build story (content elements)
            story = []
            
            # Title Page
            story.extend(self._create_title_page(project_data))
            story.append(PageBreak())
            
            # Executive Summary
            story.extend(self._create_executive_summary(project_data, reconstruction_data))
            story.append(Spacer(1, 0.5*cm))
            
            # Case Information
            story.extend(self._create_case_information(project_data))
            story.append(Spacer(1, 0.5*cm))
            
            # Methodology
            story.extend(self._create_methodology_section())
            story.append(Spacer(1, 0.5*cm))
            
            # Image Evidence
            if include_images and images_data:
                story.extend(self._create_image_section(images_data))
                story.append(Spacer(1, 0.5*cm))
            
            # GPS/Geospatial Analysis
            gps_images = [img for img in images_data if img.get('gps_latitude') and img.get('gps_longitude')]
            if gps_images:
                story.extend(self._create_gps_analysis_section(gps_images))
                story.append(Spacer(1, 0.5*cm))
            
            # 3D Reconstruction
            if reconstruction_data:
                story.extend(self._create_reconstruction_section(reconstruction_data))
                story.append(Spacer(1, 0.5*cm))
            
            # Measurements
            if include_measurements and measurements_data:
                story.extend(self._create_measurements_section(measurements_data))
                story.append(Spacer(1, 0.5*cm))
            
            # Additional Notes
            if additional_notes:
                story.extend(self._create_notes_section(additional_notes))
                story.append(Spacer(1, 0.5*cm))
            
            # Chain of Custody
            if include_audit_trail and audit_logs:
                story.extend(self._create_audit_trail_section(audit_logs))
                story.append(Spacer(1, 0.5*cm))
            
            # Certification and Signature
            story.extend(self._create_certification_section(project_data, examiner_signature))
            
            # Build PDF
            doc.build(story)
            
            logger.info(f"Report generated successfully: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error generating report: {e}")
            raise
    
    def _create_title_page(self, project_data: Dict[str, Any]) -> List:
        """Create title page"""
        elements = []
        
        # Title
        elements.append(Spacer(1, 3*cm))
        title = Paragraph(
            "FORENSIC CRIME SCENE RECONSTRUCTION REPORT",
            self.styles['CustomTitle']
        )
        elements.append(title)
        elements.append(Spacer(1, 2*cm))
        
        # Case information
        case_info = f"""
        <para align=center>
        <b>Case Number:</b> {project_data.get('case_number', 'N/A')}<br/>
        <b>Case Title:</b> {project_data.get('case_title', 'N/A')}<br/><br/>
        Prepared by: {project_data.get('examiner_name', 'N/A')}<br/>
        {project_data.get('laboratory', 'Forensic Laboratory')}<br/><br/>
        Date: {datetime.now().strftime('%d %B %Y')}
        </para>
        """
        elements.append(Paragraph(case_info, self.styles['CustomBody']))
        elements.append(Spacer(1, 3*cm))
        
        # Disclaimer
        disclaimer = Paragraph(
            "<i>This report has been prepared in accordance with Bharatiya Sakshya Adhiniyam, 2023 (Section 63 - Electronic Evidence) "
            "and follows standard forensic procedures for crime scene reconstruction.</i>",
            self.styles['CustomBody']
        )
        elements.append(disclaimer)
        
        return elements
    
    def _create_executive_summary(
        self,
        project_data: Dict[str, Any],
        reconstruction_data: Optional[Dict[str, Any]]
    ) -> List:
        """Create executive summary"""
        elements = []
        
        elements.append(Paragraph("EXECUTIVE SUMMARY", self.styles['CustomHeading']))
        
        summary_text = f"""
        This report presents the findings of a forensic crime scene reconstruction analysis conducted for 
        case {project_data.get('case_number')}. The analysis employed photogrammetric techniques to create 
        a three-dimensional representation of the crime scene from photographic evidence.
        """
        
        if reconstruction_data:
            num_points = reconstruction_data.get('num_points') or 0
            accuracy = reconstruction_data.get('estimated_accuracy_cm') or 5.0
            summary_text += f"""<br/><br/>
            The reconstruction was performed using {reconstruction_data.get('num_images_used', 0)} images, 
            resulting in a 3D model with {num_points:,} points. 
            The estimated accuracy of measurements is ±{accuracy} cm.
            """
        
        elements.append(Paragraph(summary_text, self.styles['CustomBody']))
        
        return elements
    
    def _create_case_information(self, project_data: Dict[str, Any]) -> List:
        """Create case information section"""
        elements = []
        
        elements.append(Paragraph("CASE INFORMATION", self.styles['CustomHeading']))
        
        # Create table with case details
        data = [
            ['Case Number:', project_data.get('case_number', 'N/A')],
            ['Case Title:', project_data.get('case_title', 'N/A')],
            ['Location:', project_data.get('location', 'N/A')],
            ['Incident Date:', str(project_data.get('incident_date', 'N/A'))],
            ['Examiner Name:', project_data.get('examiner_name', 'N/A')],
            ['Examiner ID:', project_data.get('examiner_id', 'N/A')],
            ['Laboratory:', project_data.get('laboratory', 'N/A')],
            ['Report Date:', datetime.now().strftime('%d %B %Y')],
        ]
        
        table = Table(data, colWidths=[5*cm, 11*cm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e3f2fd')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ]))
        
        elements.append(table)
        
        return elements
    
    def _create_methodology_section(self) -> List:
        """Create methodology section"""
        elements = []
        
        elements.append(Paragraph("METHODOLOGY", self.styles['CustomHeading']))
        
        methodology_text = """
        <b>3D Reconstruction Process:</b><br/>
        The three-dimensional reconstruction of the crime scene was performed using photogrammetric 
        Structure from Motion (SfM) techniques. This methodology involves the following steps:<br/><br/>
        
        1. <b>Image Acquisition:</b> Multiple overlapping photographs (60-80% overlap) were analyzed to ensure comprehensive coverage.<br/>
        2. <b>Feature Detection:</b> Distinctive features were automatically identified in each image using SIFT algorithm.<br/>
        3. <b>Feature Matching:</b> Corresponding features were matched across multiple images.<br/>
        4. <b>Camera Calibration:</b> Camera parameters and positions were estimated.<br/>
        5. <b>3D Point Cloud Generation:</b> Three-dimensional coordinates of scene features were calculated.<br/>
        6. <b>Mesh Reconstruction:</b> A surface mesh was created from the point cloud data.<br/>
        7. <b>Scale Calibration:</b> The model was scaled using known reference dimensions.<br/><br/>
        
        <b>Quality Assurance:</b><br/>
        All images were verified for integrity using SHA-256 cryptographic hashing. 
        Chain of custody was maintained through digital audit logs. Measurements are reported with 
        estimated uncertainty values based on reconstruction quality metrics.
        """
        
        elements.append(Paragraph(methodology_text, self.styles['CustomBody']))
        
        return elements
    
    def _create_image_section(self, images_data: List[Dict[str, Any]]) -> List:
        """Create image evidence section with comprehensive metadata"""
        elements = []
        
        elements.append(Paragraph(f"IMAGE EVIDENCE AND METADATA ({len(images_data)} Items)", self.styles['CustomHeading']))
        
        # Equipment summary
        cameras = set()
        for img in images_data:
            make = img.get('camera_make') or ''
            model = img.get('camera_model') or ''
            if make or model:
                cameras.add(f"{make} {model}".strip())
        
        if cameras:
            camera_list = ", ".join(cameras) if cameras else "Unknown"
            elements.append(Paragraph(
                f"<b>Camera Equipment:</b> {camera_list}",
                self.styles['CustomBody']
            ))
        
        # GPS summary
        gps_images = [img for img in images_data if img.get('gps_latitude') and img.get('gps_longitude')]
        if gps_images:
            lats = [img['gps_latitude'] for img in gps_images]
            lons = [img['gps_longitude'] for img in gps_images]
            center_lat = sum(lats) / len(lats)
            center_lon = sum(lons) / len(lons)
            
            elements.append(Paragraph(
                f"<b>GPS Coverage:</b> {len(gps_images)} images with coordinates. "
                f"Center point: {center_lat:.6f}°, {center_lon:.6f}°",
                self.styles['CustomBody']
            ))
        else:
            elements.append(Paragraph(
                "<b>GPS Coverage:</b> No GPS coordinates found in images.",
                self.styles['CustomBody']
            ))
        
        # Timeline summary
        dated_images = [img for img in images_data if img.get('date_taken')]
        if dated_images:
            dates = [img['date_taken'] for img in dated_images]
            earliest = min(dates)
            latest = max(dates)
            elements.append(Paragraph(
                f"<b>Capture Timeline:</b> Images captured between {earliest} and {latest}",
                self.styles['CustomBody']
            ))
        
        elements.append(Spacer(1, 0.3*cm))
        
        # Create table with comprehensive image metadata
        table_data = [['#', 'Filename', 'Camera', 'ISO', 'Shutter', 'GPS Coordinates', 'Hash (SHA-256)']]
        
        for idx, img in enumerate(images_data[:30], 1):
            gps = "N/A"
            if img.get('gps_latitude') and img.get('gps_longitude'):
                gps = f"{img['gps_latitude']:.6f}, {img['gps_longitude']:.6f}"
            
            camera = "N/A"
            if img.get('camera_model'):
                camera = img['camera_model'][:15]
            elif img.get('camera_make'):
                camera = img['camera_make'][:15]
            
            table_data.append([
                str(idx),
                img.get('filename', 'N/A')[:18],
                camera,
                str(img.get('iso', 'N/A')),
                str(img.get('exposure_time', 'N/A')),
                gps,
                img.get('file_hash', 'N/A')[:12] + '..'
            ])
        
        table = Table(table_data, colWidths=[0.8*cm, 3.2*cm, 2.5*cm, 1.2*cm, 1.8*cm, 4.5*cm, 2.5*cm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0d47a1')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 7),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#e3f2fd')]),
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 0.5*cm))
        return elements
    
    def _create_gps_analysis_section(self, gps_images: List[Dict[str, Any]]) -> List:
        """Create GPS/Geospatial analysis section with real coordinate data"""
        elements = []
        
        elements.append(Paragraph("GEOSPATIAL ANALYSIS", self.styles['CustomHeading']))
        
        # Calculate scene bounds and statistics
        lats = [img['gps_latitude'] for img in gps_images]
        lons = [img['gps_longitude'] for img in gps_images]
        alts = [img.get('gps_altitude') for img in gps_images if img.get('gps_altitude')]
        
        min_lat, max_lat = min(lats), max(lats)
        min_lon, max_lon = min(lons), max(lons)
        center_lat = sum(lats) / len(lats)
        center_lon = sum(lons) / len(lons)
        
        # Calculate approximate scene span using Haversine
        import math
        lat_span_km = abs(max_lat - min_lat) * 111.32  # 1 degree lat ≈ 111.32 km
        lon_span_km = abs(max_lon - min_lon) * 111.32 * math.cos(math.radians(center_lat))
        
        intro_text = f"""
        All GPS coordinates were extracted directly from image EXIF metadata. The following analysis 
        describes the geographic distribution of evidence photographs at the crime scene.
        """
        elements.append(Paragraph(intro_text, self.styles['CustomBody']))
        
        # Scene bounds table
        bounds_data = [
            ['GPS Parameter', 'Value'],
            ['Center Point (Lat)', f"{center_lat:.8f}°"],
            ['Center Point (Lon)', f"{center_lon:.8f}°"],
            ['Northern Bound', f"{max_lat:.8f}°"],
            ['Southern Bound', f"{min_lat:.8f}°"],
            ['Eastern Bound', f"{max_lon:.8f}°"],
            ['Western Bound', f"{min_lon:.8f}°"],
            ['Scene Span (N-S)', f"{lat_span_km*1000:.2f} meters"],
            ['Scene Span (E-W)', f"{lon_span_km*1000:.2f} meters"],
            ['Images with GPS', str(len(gps_images))],
        ]
        
        if alts:
            min_alt, max_alt = min(alts), max(alts)
            bounds_data.append(['Altitude Range', f"{min_alt:.1f}m - {max_alt:.1f}m"])
        
        table = Table(bounds_data, colWidths=[6*cm, 10*cm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2e7d32')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('BACKGROUND', (0, 1), (0, -1), colors.HexColor('#e8f5e9')),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 0.3*cm))
        
        # Individual coordinates table
        elements.append(Paragraph("<b>Individual Image Coordinates:</b>", self.styles['CustomBody']))
        
        coord_data = [['#', 'Filename', 'Latitude', 'Longitude', 'Altitude', 'Date/Time']]
        for idx, img in enumerate(gps_images[:20], 1):
            alt_str = f"{img.get('gps_altitude'):.1f}m" if img.get('gps_altitude') else "N/A"
            date_str = str(img.get('date_taken', 'N/A'))[:19] if img.get('date_taken') else "N/A"
            coord_data.append([
                str(idx),
                img.get('filename', 'N/A')[:20],
                f"{img['gps_latitude']:.8f}°",
                f"{img['gps_longitude']:.8f}°",
                alt_str,
                date_str
            ])
        
        coord_table = Table(coord_data, colWidths=[0.8*cm, 3.5*cm, 3*cm, 3*cm, 2*cm, 4*cm])
        coord_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1565c0')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 7),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#e3f2fd')]),
        ]))
        
        elements.append(coord_table)
        
        return elements
    
    def _create_reconstruction_section(self, reconstruction_data: Dict[str, Any]) -> List:
        """Create 3D reconstruction section"""
        elements = []
        
        elements.append(Paragraph("3D RECONSTRUCTION RESULTS", self.styles['CustomHeading']))
        
        # Handle None values safely
        num_points = reconstruction_data.get('num_points') or 0
        num_faces = reconstruction_data.get('num_faces') or 0
        scale_factor = reconstruction_data.get('scale_factor') or 1.0
        accuracy = reconstruction_data.get('estimated_accuracy_cm')
        quality = reconstruction_data.get('quality') or 'N/A'
        
        # Reconstruction statistics
        data = [
            ['Images Used:', str(reconstruction_data.get('num_images_used', 'N/A'))],
            ['Point Cloud Points:', f"{num_points:,}"],
            ['Mesh Faces:', f"{num_faces:,}"],
            ['Scale Factor:', f"{scale_factor:.4f} meters/unit"],
            ['Estimated Accuracy:', f"±{accuracy} cm" if accuracy else 'N/A'],
            ['Processing Quality:', quality.upper() if quality != 'N/A' else 'N/A'],
        ]
        
        table = Table(data, colWidths=[6*cm, 10*cm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e8f5e9')),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
        ]))
        
        elements.append(table)
        
        return elements
    
    def _create_measurements_section(self, measurements_data: List[Dict[str, Any]]) -> List:
        """Create measurements section"""
        elements = []
        
        elements.append(Paragraph(f"MEASUREMENTS ({len(measurements_data)} Total)", self.styles['CustomHeading']))
        
        # Measurements table
        table_data = [['#', 'Type', 'Name', 'Value', 'Uncertainty']]
        
        for idx, meas in enumerate(measurements_data, 1):
            value = meas.get('value')
            unit = meas.get('unit') or 'm'
            uncertainty = meas.get('uncertainty')
            value_str = f"{value:.3f} {unit}" if value is not None else "N/A"
            uncertainty_str = f"±{uncertainty:.3f} {unit}" if uncertainty is not None else "N/A"
            table_data.append([
                str(idx),
                meas.get('measurement_type', 'N/A'),
                meas.get('name', 'N/A')[:25],
                value_str,
                uncertainty_str
            ])
        
        table = Table(table_data, colWidths=[1*cm, 3*cm, 6*cm, 3*cm, 3*cm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1976d2')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f5f5')]),
        ]))
        
        elements.append(table)
        
        return elements
    
    def _create_notes_section(self, notes: str) -> List:
        """Create additional notes section"""
        elements = []
        
        elements.append(Paragraph("ADDITIONAL NOTES AND OBSERVATIONS", self.styles['CustomHeading']))
        elements.append(Paragraph(notes, self.styles['CustomBody']))
        
        return elements
    
    def _create_audit_trail_section(self, audit_logs: List[Dict[str, Any]]) -> List:
        """Create chain of custody section"""
        elements = []
        
        elements.append(Paragraph("SYSTEM CHANGE LOG & AUDIT TRAIL", self.styles['CustomHeading']))
        elements.append(Paragraph(
            "The following section logs all user interactions, modifications, and system events with high-precision timestamps. "
            "Any adjustments to lighting, cropping, or measurement parameters are recorded here for forensic accountability.",
            self.styles['CustomBody']
        ))
        
        # Audit log table
        table_data = [['Timestamp (UTC)', 'Event Type', 'User / Action', 'Details / Resource Affected']]
        
        for log in audit_logs:
            table_data.append([
                str(log.get('timestamp', 'N/A'))[:19],
                log.get('event_type', 'N/A').upper(),
                log.get('user_name', 'N/A'),
                log.get('event_description', 'N/A')[:50]
            ])
        
        table = Table(table_data, colWidths=[4*cm, 4*cm, 3*cm, 5.5*cm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#212121')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f5f5')]),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        elements.append(table)
        
        return elements
    
    def _create_certification_section(
        self,
        project_data: Dict[str, Any],
        examiner_signature: Optional[str]
    ) -> List:
        """Create certification and signature section"""
        elements = []
        
        elements.append(PageBreak())
        elements.append(Paragraph("CERTIFICATION", self.styles['CustomHeading']))
        
        certification_text = f"""
        I, {project_data.get('examiner_name', '[Examiner Name]')}, hereby certify that:<br/><br/>
        
        1. The analysis presented in this report was conducted using scientifically accepted methods 
           and procedures for crime scene reconstruction.<br/>
        2. All evidence images were verified for integrity using cryptographic hashing.<br/>
        3. Chain of custody was maintained throughout the analysis process.<br/>
        4. Measurements and calculations were performed with due care and professional competence.<br/>
        5. This report has been prepared in accordance with the Bharatiya Sakshya Adhiniyam, 2023 (Section 63).<br/><br/>
        
        <b>Report Generated:</b> {datetime.now().strftime('%d %B %Y at %H:%M:%S UTC')}<br/>
        <b>System Version:</b> {settings.APP_VERSION}<br/>
        <b>Report Hash (SHA-256):</b> [Will be calculated after generation]<br/><br/>
        
        Digitally generated report by Crime Scene Reconstruction System.
        """
        
        elements.append(Paragraph(certification_text, self.styles['CustomBody']))
        elements.append(Spacer(1, 2*cm))
        
        # Signature line
        signature_text = f"""
        <para align=left>
        _________________________<br/>
        {project_data.get('examiner_name', '[Examiner Name]')}<br/>
        {project_data.get('examiner_id', '[Examiner ID]')}<br/>
        {project_data.get('laboratory', '[Laboratory Name]')}
        </para>
        """
        elements.append(Paragraph(signature_text, self.styles['CustomBody']))
        
        return elements
