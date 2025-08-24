# Sustainability Dashboard (Textile) — Full Stack

This project contains a React (Vite) + Tailwind frontend and a FastAPI backend with SQLite mock data.

## Prerequisites
- Python 3.10+
- Node.js 18+ and npm

## Run Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```
Backend will run at http://127.0.0.1:8000

## Run Frontend
```bash
cd frontend
npm install
npm run dev
```
Frontend will run at http://localhost:5173

## Build Frontend (optional)
```bash
npm run build
npm run preview
```

## Features Implemented
- KPI tiles (Energy, Water, Waste, Emissions) + Overall score
- Filters (date range, department/unit basic support)
- Alerts panel
- Insights page per KPI: trend, hotspots, anomalies, cost impact, goal progress
- Export CSV/PDF
- Auto refresh + manual refresh button

> Authentication, action-tracker, custom rules, email summaries, etc., are omitted to keep the assignment focused and easy to run.
