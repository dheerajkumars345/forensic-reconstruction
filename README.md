# Crime Scene Reconstruction System

A comprehensive forensic-grade crime scene reconstruction software that uses photogrammetry to convert multiple overlapping images (60-80% superimposition) into accurate 3D models with georeferencing, measurement tools, and compliant reporting for the Indian judiciary system.

## 🎯 Features

### Core Capabilities
- **Photogrammetric 3D Reconstruction**: Structure from Motion (SfM) pipeline using OpenCV and COLMAP
- **Accurate Measurements**: Distance, area, volume, and angle measurements with uncertainty estimation
- **GPS Integration**: Extract GPS coordinates from image EXIF data and visualize on satellite maps
- **Forensic Reports**: Generate PDF reports compliant with Indian Evidence Act Section 65B
- **Chain of Custody**: Complete audit trail with cryptographic hash verification
- **Image Processing**: EXIF metadata extraction, quality assessment, and feature detection

### Technical Stack

#### Backend (Python)
- **Framework**: FastAPI (async REST API)
- **Image Processing**: OpenCV, Pillow, piexif
- **Photogrammetry**: OpenCV (SfM), COLMAP integration
- **3D Processing**: Open3D (point clouds, mesh reconstruction)
- **Geospatial**: geopy, pyproj, folium
- **Reports**: ReportLab (PDF generation)
- **Database**: SQLAlchemy with SQLite/PostgreSQL

#### Frontend (React + TypeScript)
- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite
- **UI Library**: Material-UI (MUI)
- **3D Visualization**: Three.js with React Three Fiber
- **Maps**: Leaflet with React-Leaflet
- **State Management**: Zustand
- **File Upload**: React Dropzone

## 📋 Prerequisites

### Backend Requirements
- Python 3.9 or higher
- pip (Python package manager)
- Optional: COLMAP (for high-quality reconstruction)

### Frontend Requirements
- Node.js 18 or higher
- npm or yarn

## 🚀 Installation

### Backend Setup

1. **Navigate to backend directory**:
   ```bash
   cd backend
   ```

2. **Create virtual environment** (recommended):
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the backend server**:
   ```bash
   python main.py
   ```

   The backend API will be available at `http://localhost:8000`

### Frontend Setup

1. **Navigate to frontend directory**:
   ```bash
   cd frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Run the development server**:
   ```bash
   npm run dev
   ```

   The frontend will be available at `http://localhost:3000`

## 📖 Usage Guide

### Creating a New Case

1. Open the application at `http://localhost:3000`
2. Click "New Case" button
3. Fill in the case information:
   - Case Number (required)
   - Case Title (required)
   - Description
   - Location
   - Examiner Name (required)
   - Examiner ID
   - Laboratory Name

### Uploading Images

1. Open a case from the cases list
2. Navigate to the "Images" tab
3. Drag and drop images or click to browse
4. Supported formats: JPG, JPEG, PNG, TIF, TIFF
5. Images should have 60-80% overlap for best reconstruction results

### 3D Reconstruction

1. Upload at least 2 images (10+ recommended for best results)
2. Navigate to the "3D Model" tab
3. Click "Start Reconstruction"
4. Wait for processing to complete
5. View the reconstructed 3D model

### Taking Measurements

1. Complete 3D reconstruction first
2. Navigate to the "Measurements" tab
3. Click "Add Measurement"
4. Select measurement type:
   - Distance (between two points)
   - Area (polygon)
   - Volume (convex hull)
   - Angle (three points)
   - Trajectory (for ballistics)

### Generating Reports

1. Navigate to the "Report" tab
2. Click "Generate PDF Report"
3. The report will include:
   - Case information
   - Image evidence with metadata
   - 3D reconstruction details
   - Measurements table
   - Chain of custody log
   - Examiner certification

## 🔧 Configuration

### Backend Configuration

Edit `backend/config.py` to customize:

- File upload limits
- Image quality thresholds
- Reconstruction quality settings
- Measurement precision
- Report templates
- Forensic compliance settings

### Frontend Configuration

Create `frontend/.env`:

```env
VITE_API_BASE_URL=http://localhost:8000/api
```

## 📁 Project Structure

```
forensic-antigravity/
├── backend/
│   ├── main.py                 # FastAPI application entry
│   ├── config.py               # Configuration settings
│   ├── models.py               # Database and API models
│   ├── requirements.txt        # Python dependencies
│   ├── database/
│   │   └── __init__.py         # Database connection
│   ├── services/
│   │   ├── chain_of_custody.py # Audit logging
│   │   ├── image_processor.py  # Image processing
│   │   ├── photogrammetry.py   # 3D reconstruction
│   │   ├── reconstruction_3d.py # Mesh processing
│   │   ├── geospatial.py       # GPS and mapping
│   │   ├── measurement.py      # Measurements
│   │   └── report_generator.py # PDF reports
│   └── routes/
│       ├── projects.py         # Project endpoints
│       ├── images.py           # Image endpoints
│       ├── reconstruction.py   # Reconstruction endpoints
│       ├── measurements.py     # Measurement endpoints
│       └── reports.py          # Report endpoints
│
└── frontend/
    ├── package.json
    ├── vite.config.ts
    ├── tsconfig.json
    ├── index.html
    └── src/
        ├── main.tsx            # React entry point
        ├── App.tsx             # Main app component
        ├── api/
        │   └── client.ts       # API client
        ├── pages/
        │   ├── ProjectsPage.tsx
        │   └── ProjectDetailPage.tsx
        └── components/
            ├── Header.tsx
            ├── ImageUploadPanel.tsx
            ├── ModelViewer.tsx
            ├── MapView.tsx
            ├── MeasurementsPanel.tsx
            └── ReportPanel.tsx
```

## 🔒 Forensic Compliance

This system implements forensic best practices:

- **SHA-256 Hashing**: All uploaded images are hashed for integrity verification
- **Chain of Custody**: Complete audit trail of all operations
- **Timestamp Verification**: All events are timestamped
- **Metadata Preservation**: Original EXIF data is preserved
- **Evidence Act Compliance**: Reports follow Indian Evidence Act Section 65B requirements
- **Digital Signatures**: Reports can be digitally signed

## 🧪 Testing

### Backend Tests

```bash
cd backend
pytest
```

### Frontend Tests

```bash
cd frontend
npm test
```

## 🎓 For Forensic Students

This system is designed as an educational and practical tool for forensic physics and ballistics students. Key learning areas:

- **Photogrammetry Principles**: Understand Structure from Motion algorithms
- **3D Reconstruction**: Learn point cloud processing and mesh generation
- **Measurement Accuracy**: Practice calibration and uncertainty estimation
- **Forensic Documentation**: Proper evidence handling and reporting
- **Chain of Custody**: Maintain integrity of digital evidence

## ⚠️ Important Notes

1. **Calibration**: Always use a reference object with known dimensions for scale calibration
2. **Image Quality**: Use high-resolution images (minimum 1024x768)
3. **Overlap**: Ensure 60-80% overlap between consecutive images
4. **Lighting**: Consistent lighting conditions produce better results
5. **COLMAP**: For production use, install COLMAP for high-quality reconstruction

## 📚 Additional Resources

- [OpenCV Documentation](https://docs.opencv.org/)
- [Open3D Documentation](http://www.open3d.org/docs/)
- [COLMAP Documentation](https://colmap.github.io/)
- [Indian Evidence Act](https://legislative.gov.in/)

## 🤝 Contributing

This is an educational project. Improvements and contributions are welcome!

## 📄 License

This project is created for educational purposes.

## 👨‍🔬 Author

Created for forensic physics and ballistics students as a final year project tool.

## 🆘 Support

For issues or questions:
1. Check the documentation
2. Review the code comments
3. Test with sample datasets
4. Verify all dependencies are installed

## 🔄 Future Enhancements

- [ ] Real-time reconstruction preview
- [ ] Multi-user collaboration
- [ ] Advanced trajectory analysis for ballistics
- [ ] Integration with forensic databases
- [ ] Mobile app for field evidence collection
- [ ] AI-assisted feature matching
- [ ] Cloud deployment options
