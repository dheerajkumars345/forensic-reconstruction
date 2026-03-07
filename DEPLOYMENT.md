# Forensic Crime Scene Reconstruction System

## Project Structure

```
forensic-antigravity/
├── backend/          # FastAPI Python backend
├── frontend/         # React/Vite TypeScript frontend
└── README.md
```

## Deployment

### Frontend (Vercel)

1. **Connect to Vercel:**
   - Go to [vercel.com](https://vercel.com) and sign in
   - Click "Add New Project"
   - Import your GitHub repository

2. **Configure the project:**
   - Root Directory: `frontend`
   - Framework Preset: Vite
   - Build Command: `npm run build`
   - Output Directory: `dist`

3. **Set Environment Variables:**
   - `VITE_API_BASE_URL`: Your backend API URL (e.g., `https://your-backend.railway.app/api`)

4. **Deploy:**
   - Click "Deploy"

### Backend (Railway)

1. **Connect to Railway:**
   - Go to [railway.app](https://railway.app) and sign in
   - Click "New Project" → "Deploy from GitHub repo"
   - Select your repository

2. **Configure the project:**
   - Root Directory: `backend`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

3. **Set Environment Variables:**

   ```
   FRONTEND_URL=https://your-app.vercel.app
   CORS_ALLOW_ALL=false
   DEBUG=false
   ```

4. **Deploy:**
   - Railway will automatically deploy

### Alternative: Render

1. **Create a new Web Service** on [render.com](https://render.com)
2. Connect your GitHub repository
3. Configure:
   - Root Directory: `backend`
   - Build Command: `pip install -r requirements-deploy.txt`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

## Local Development

### Backend

```bash
cd backend
python -m venv .venv
.venv/Scripts/activate  # Windows
source .venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Environment Variables

### Frontend (.env)

```
VITE_API_BASE_URL=http://localhost:8000/api
```

### Backend (.env)

```
DEBUG=true
FRONTEND_URL=http://localhost:3000
CORS_ALLOW_ALL=false
```

## API Documentation

Once the backend is running, visit:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
