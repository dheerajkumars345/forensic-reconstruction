# Quick Start Guide

## Installation

Run the setup script:

```powershell
.\setup.ps1
```

This will:
1. Check Python and Node.js installation
2. Create Python virtual environment
3. Install all backend dependencies
4. Install all frontend dependencies

## Running the Application

### Option 1: Using PowerShell (Recommended)

**Terminal 1 - Backend:**
```powershell
cd backend
.\venv\Scripts\Activate.ps1
python main.py
```

**Terminal 2 - Frontend:**
```powershell
cd frontend
npm run dev
```

### Option 2: Manual Setup

**Backend:**
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
python main.py
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

## Access Points

- **Frontend Application**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **API Redoc**: http://localhost:8000/redoc

## First Steps

1. Open http://localhost:3000
2. Click "New Case" to create your first forensic case
3. Fill in case details (case number, title, examiner name)
4. Upload crime scene images (10+ images recommended, 60-80% overlap)
5. Navigate through tabs to explore features

## Troubleshooting

### Backend Issues

- **Port 8000 already in use**: Change port in `backend/main.py`
- **Import errors**: Activate virtual environment first
- **Database errors**: Delete `backend/data/forensic.db` and restart

### Frontend Issues

- **Port 3000 already in use**: Vite will automatically try port 3001
- **API connection errors**: Ensure backend is running on port 8000
- **Build errors**: Delete `node_modules` and run `npm install` again

## Sample Workflow

1. **Create Case**: Case #2024-001, "Crime Scene Alpha"
2. **Upload Images**: 10-15 photos with good overlap
3. **Start Reconstruction**: Click "Start Reconstruction" in 3D Model tab
4. **Add Measurements**: After reconstruction, take distance measurements
5. **Generate Report**: Create PDF report in Reports tab

## Tips for Best Results

- Use high-resolution images (2MP or higher)
- Ensure 60-80% overlap between consecutive images
- Include a reference object with known dimensions for scale calibration
- Take photos from multiple angles around the scene
- Use consistent lighting conditions

## Need Help?

- Check [README.md](../README.md) for detailed documentation
- Review [walkthrough.md](walkthrough.md) for technical details
- API documentation available at http://localhost:8000/docs
