from fastapi import FastAPI, Query, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta, date
import os
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from jinja2 import Template
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data.db")

app = FastAPI(title="Sustainability API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_engine() -> Engine:
    return create_engine(DATABASE_URL, future=True)

def seed_db(engine: Engine):
    with engine.begin() as conn:
        conn.exec_driver_sql("""
        CREATE TABLE IF NOT EXISTS metrics (
            id INTEGER PRIMARY KEY,
            ts DATE NOT NULL,
            department TEXT,
            unit TEXT,
            shift TEXT,
            energy_kwh REAL,
            water_l REAL,
            waste_kg REAL,
            emissions_gco2 REAL
        );
        """)
        conn.exec_driver_sql("""
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY,
            created_at DATE NOT NULL,
            title TEXT,
            message TEXT,
            severity TEXT,
            metric TEXT
        );
        """)
        conn.exec_driver_sql("""
        CREATE TABLE IF NOT EXISTS goals (
            id INTEGER PRIMARY KEY,
            metric TEXT,
            target REAL,
            period TEXT,
            baseline REAL,
            start_date DATE,
            due_date DATE
        );
        """)

    # If metrics empty, generate mock data for last 180 days
    with engine.begin() as conn:
        count = conn.exec_driver_sql("SELECT COUNT(*) FROM metrics").scalar()
        if count == 0:
            start = date.today() - timedelta(days=180)
            departments = ["Spinning", "Weaving", "Dyeing"]
            units = ["Unit A", "Unit B"]
            shifts = ["Morning", "Evening", "Night"]
            rows = []
            import random
            for d in range(181):
                day = start + timedelta(days=d)
                for dep in departments:
                    for u in units:
                        for s in shifts:
                            # Base values per department with some variance
                            base_energy = {"Spinning": 1200, "Weaving": 900, "Dyeing": 1500}[dep]
                            base_water = {"Spinning": 6000, "Weaving": 4000, "Dyeing": 10000}[dep]
                            base_waste = {"Spinning": 180, "Weaving": 140, "Dyeing": 220}[dep]
                            base_em = {"Spinning": 140, "Weaving": 110, "Dyeing": 200}[dep]
                            mult = 0.85 + random.random()*0.4  # 0.85 - 1.25
                            rows.append((day, dep, u, s,
                                         round(base_energy*mult + random.uniform(-40,40),2),
                                         round(base_water*mult + random.uniform(-300,300),2),
                                         round(base_waste*mult + random.uniform(-12,12),2),
                                         round(base_em*mult + random.uniform(-10,10),2)))
            df = pd.DataFrame(rows, columns=["ts","department","unit","shift","energy_kwh","water_l","waste_kg","emissions_gco2"])
            df.to_sql("metrics", conn.connection, if_exists="append", index=False)

        alert_count = conn.exec_driver_sql("SELECT COUNT(*) FROM alerts").scalar()
        if alert_count == 0:
            alerts = [
                (date.today(), "High Energy Consumption", "Energy usage is 75% above limit in Dyeing", "critical", "energy"),
                (date.today()-timedelta(days=1), "Maintenance Scheduled", "Chiller maintenance on Tuesday", "info", "overall"),
                (date.today()-timedelta(days=3), "Policy Update", "New wastewater guidelines effective immediately", "warning", "water")
            ]
            df = pd.DataFrame(alerts, columns=["created_at","title","message","severity","metric"])
            df.to_sql("alerts", conn.connection, if_exists="append", index=False)

        goals_count = conn.exec_driver_sql("SELECT COUNT(*) FROM goals").scalar()
        if goals_count == 0:
            goals = [
                ("energy", 0.90, "yearly", 1.00, date.today()-timedelta(days=30), date.today()+timedelta(days=335)),
                ("water", 0.88, "yearly", 1.00, date.today()-timedelta(days=30), date.today()+timedelta(days=335)),
                ("waste", 0.92, "yearly", 1.00, date.today()-timedelta(days=30), date.today()+timedelta(days=335)),
                ("emissions", 0.85, "yearly", 1.00, date.today()-timedelta(days=30), date.today()+timedelta(days=335)),
            ]
            df = pd.DataFrame(goals, columns=["metric","target","period","baseline","start_date","due_date"])
            df.to_sql("goals", conn.connection, if_exists="append", index=False)

engine = get_engine()
seed_db(engine)

def parse_dates(start: Optional[str], end: Optional[str]):
    if start:
        start_dt = datetime.fromisoformat(start).date()
    else:
        start_dt = date.today() - timedelta(days=29)
    if end:
        end_dt = datetime.fromisoformat(end).date()
    else:
        end_dt = date.today()
    return start_dt, end_dt

def query_df(engine: Engine, start: date, end: date, department: Optional[str] = None, unit: Optional[str] = None):
    params = {"start": start, "end": end}
    filters = "ts BETWEEN :start AND :end"
    if department:
        filters += " AND department = :department"
        params["department"] = department
    if unit:
        filters += " AND unit = :unit"
        params["unit"] = unit
    sql = f"SELECT * FROM metrics WHERE {filters}"
    return pd.read_sql(text(sql), engine, params=params, parse_dates=["ts"])

@app.get("/api/kpis")
def get_kpis(start: Optional[str] = None, end: Optional[str] = None,
             department: Optional[str] = Query(None), unit: Optional[str] = Query(None)):
    start_dt, end_dt = parse_dates(start, end)
    df = query_df(engine, start_dt, end_dt, department, unit)
    if df.empty:
        return {"kpis": {}, "overall": {"score": 0, "status": "No data"}}
    # compute sums
    sums = df[["energy_kwh","water_l","waste_kg","emissions_gco2"]].sum().to_dict()
    # simple status flags
    status = {
        "energy": "On Track" if sums["energy_kwh"] < 1.2*df["energy_kwh"].mean()*len(df.index.unique()) else "Over Limit",
        "water": "On Track" if sums["water_l"] < 1.2*df["water_l"].mean()*len(df.index.unique()) else "Over Limit",
        "waste": "On Track" if sums["waste_kg"] < 1.2*df["waste_kg"].mean()*len(df.index.unique()) else "Over Limit",
        "emissions": "On Track" if sums["emissions_gco2"] < 1.2*df["emissions_gco2"].mean()*len(df.index.unique()) else "Over Limit",
    }
    # overall score: normalized inverse of z-scores (toy metric 0-100)
    import numpy as np
    metrics = ["energy_kwh","water_l","waste_kg","emissions_gco2"]
    z = []
    for m in metrics:
        z.append((sums[m]-df[m].mean()*len(df.index.unique()))/(df[m].std()+1e-6))
    score = max(0, 100 - float(np.mean(np.abs(z)))*10)
    return {
        "kpis": {
            "energy": {"value": round(sums["energy_kwh"],2), "status": status["energy"], "unit":"kWh"},
            "water": {"value": round(sums["water_l"],2), "status": status["water"], "unit":"L"},
            "waste": {"value": round(sums["waste_kg"],2), "status": status["waste"], "unit":"kg"},
            "emissions": {"value": round(sums["emissions_gco2"],2), "status": status["emissions"], "unit":"gCO2"},
        },
        "overall": {"score": round(score,1), "status": "On Track" if score>=60 else "Watch" if score>=40 else "Critical"}
    }

@app.get("/api/insights/{metric}")
def insights(metric: str, start: Optional[str] = None, end: Optional[str] = None,
             department: Optional[str] = None, unit: Optional[str] = None, group_by: Optional[str] = "department"):
    start_dt, end_dt = parse_dates(start, end)
    df = query_df(engine, start_dt, end_dt, department, unit)
    if df.empty:
        return {"trend": [], "hotspots": [], "anomalies": [], "cost_impact": {}, "goal": {}}
    metric_map = {
        "energy":"energy_kwh","water":"water_l","waste":"waste_kg","emissions":"emissions_gco2","overall":"energy_kwh"
    }
    col = metric_map.get(metric, "energy_kwh")

    # Trend
    trend = (df.groupby("ts")[col].sum()
             .reset_index()
             .rename(columns={"ts":"date", col:"value"}))
    trend["date"] = trend["date"].astype(str)

    # Hotspots
    gb = group_by if group_by in ["department","unit","shift"] else "department"
    hotspots = (df.groupby(gb)[col].sum().reset_index().rename(columns={gb:"label", col:"value"})).to_dict(orient="records")

    # Anomalies via simple z-score
    s = (df.groupby("ts")[col].sum()).reset_index()
    m, sd = s[col].mean(), s[col].std() + 1e-6
    s["z"] = (s[col]-m)/sd
    anomalies = s.loc[s["z"].abs()>2][["ts", col, "z"]]
    anomalies = [{"date": str(r["ts"].date()), "value": float(r[col]), "z": float(r["z"])} for _, r in anomalies.iterrows()]

    # Cost impact (toy conversion factors)
    factor = {"energy_kwh":0.12, "water_l":0.001, "waste_kg":0.25, "emissions_gco2":0.0}.get(col, 0.1)
    total = float(df[col].sum())
    est_cost = round(total * factor, 2)

    # Goal progress
    with engine.begin() as conn:
        g = pd.read_sql("SELECT * FROM goals WHERE metric = :m", conn.connection, params={"m": metric if metric!="overall" else "energy"})
    goal = {}
    if not g.empty:
        target_ratio = float(g["target"].iloc[0])
        baseline = float(g["baseline"].iloc[0])
        # naive progress: assume we want to reduce to target_ratio of baseline
        baseline_total = baseline * total
        target_total = target_ratio * baseline_total
        progress = max(0.0, min(1.0, 1 - (total/ baseline_total))) if baseline_total>0 else 0.0
        goal = {
            "target_ratio": target_ratio,
            "progress": round(progress, 2),
            "due_date": str(pd.to_datetime(g["due_date"].iloc[0]).date())
        }

    return {"trend": trend.to_dict(orient="records"),
            "hotspots": hotspots,
            "anomalies": anomalies,
            "cost_impact": {"estimated_cost": est_cost, "currency":"USD"},
            "goal": goal
            }

@app.get("/api/alerts")
def get_alerts():
    with engine.begin() as conn:
        df = pd.read_sql("SELECT * FROM alerts ORDER BY created_at DESC", conn.connection, parse_dates=["created_at"])
    return [{"id": int(r["id"]), "title": r["title"], "message": r["message"],
             "severity": r["severity"], "date": str(r["created_at"].date()), "metric": r["metric"]} for _, r in df.iterrows()]

@app.get("/api/export/csv")
def export_csv(metric: str = "overall", start: Optional[str] = None, end: Optional[str] = None):
    start_dt, end_dt = parse_dates(start, end)
    df = query_df(engine, start_dt, end_dt)
    if metric != "overall":
        col = {"energy":"energy_kwh","water":"water_l","waste":"waste_kg","emissions":"emissions_gco2"}.get(metric, "energy_kwh")
        df = df[["ts","department","unit","shift", col]].rename(columns={col: metric})
    out = df.to_csv(index=False)
    return Response(content=out, media_type="text/csv",
                    headers={"Content-Disposition": f"attachment; filename={metric}_export.csv"})

@app.get("/api/export/pdf")
def export_pdf(metric: str = "overall", start: Optional[str] = None, end: Optional[str] = None,
               notes: Optional[str] = "", brand: Optional[str] = "Sustainability Inc."):
    start_dt, end_dt = parse_dates(start, end)
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    c.setFont("Helvetica-Bold", 16)
    c.drawString(2*cm, height-2*cm, f"{brand} - {metric.capitalize()} Report")
    c.setFont("Helvetica", 10)
    c.drawString(2*cm, height-2.7*cm, f"Period: {start_dt} to {end_dt}")
    c.drawString(2*cm, height-3.2*cm, f"Generated: {date.today()}")
    # Simple summary numbers
    df = query_df(engine, start_dt, end_dt)
    totals = {
        "Energy (kWh)": round(df["energy_kwh"].sum(),2),
        "Water (L)": round(df["water_l"].sum(),2),
        "Waste (kg)": round(df["waste_kg"].sum(),2),
        "Emissions (gCO2)": round(df["emissions_gco2"].sum(),2),
    }
    y = height-4.2*cm
    for k,v in totals.items():
        c.drawString(2*cm, y, f"{k}: {v}")
        y -= 0.6*cm
    if notes:
        c.drawString(2*cm, y-0.3*cm, f"Notes: {notes[:120]}")
    c.showPage()
    c.save()
    pdf = buffer.getvalue()
    buffer.close()
    return Response(pdf, media_type="application/pdf",
                    headers={"Content-Disposition": f"attachment; filename={metric}_report.pdf"})
