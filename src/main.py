"""MyCoach — FastAPI entry point."""
import os
import sqlite3
from pathlib import Path
from typing import List, Optional
from datetime import date, datetime

from fastapi import FastAPI, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware

from models.schemas import (
    Client, ClientCreate, ClientUpdate,
    Session, SessionCreate,
    Payment, PaymentCreate,
    DashboardStats
)

# ── App setup ────────────────────────────────────────────────

app = FastAPI(title="MyCoach", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH = Path(__file__).parent.parent / "data" / "mycoach.db"


# ── Database init ────────────────────────────────────────────

def init_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT,
            phone TEXT,
            notes TEXT,
            hourly_rate REAL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER NOT NULL,
            date DATE NOT NULL,
            duration_minutes INTEGER NOT NULL,
            notes TEXT,
            billed INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (client_id) REFERENCES clients(id)
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER NOT NULL,
            date DATE NOT NULL,
            amount REAL NOT NULL,
            method TEXT,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (client_id) REFERENCES clients(id)
        )
    """)

    conn.commit()
    conn.close()


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


@app.on_event("startup")
def startup():
    init_db()


# ── Static UI ────────────────────────────────────────────────

UI_DIR = Path(__file__).parent / "ui"

@app.get("/", response_class=HTMLResponse)
def index():
    return FileResponse(UI_DIR / "index.html")

@app.get("/login", response_class=HTMLResponse)
def login_page():
    return FileResponse(UI_DIR / "login.html")

app.mount("/ui", StaticFiles(directory=str(UI_DIR)), name="ui")


# ── Clients ──────────────────────────────────────────────────

@app.get("/api/clients", response_model=List[dict])
def list_clients(db: sqlite3.Connection = Depends(get_db)):
    rows = db.execute("""
        SELECT c.*,
            COALESCE(SUM(s.duration_minutes) / 60.0, 0) AS total_hours,
            COALESCE(SUM(CASE WHEN s.billed THEN s.duration_minutes / 60.0 * c.hourly_rate ELSE 0 END), 0) AS total_revenue,
            COALESCE((SELECT SUM(p.amount) FROM payments p WHERE p.client_id = c.id), 0) AS total_paid
        FROM clients c
        LEFT JOIN sessions s ON s.client_id = c.id
        GROUP BY c.id
        ORDER BY c.name
    """).fetchall()
    result = []
    for r in rows:
        d = dict(r)
        d["balance"] = d["total_revenue"] - d["total_paid"]
        result.append(d)
    return result


@app.post("/api/clients", response_model=dict)
def create_client(client: ClientCreate, db: sqlite3.Connection = Depends(get_db)):
    c = db.execute(
        "INSERT INTO clients (name, email, phone, notes, hourly_rate) VALUES (?,?,?,?,?)",
        (client.name, client.email, client.phone, client.notes, client.hourly_rate or 0)
    )
    db.commit()
    return {"id": c.lastrowid, "message": "Client créé"}


@app.get("/api/clients/{client_id}", response_model=dict)
def get_client(client_id: int, db: sqlite3.Connection = Depends(get_db)):
    row = db.execute("SELECT * FROM clients WHERE id = ?", (client_id,)).fetchone()
    if not row:
        raise HTTPException(404, "Client introuvable")
    return dict(row)


@app.put("/api/clients/{client_id}")
def update_client(client_id: int, client: ClientUpdate, db: sqlite3.Connection = Depends(get_db)):
    db.execute(
        "UPDATE clients SET name=?, email=?, phone=?, notes=?, hourly_rate=? WHERE id=?",
        (client.name, client.email, client.phone, client.notes, client.hourly_rate or 0, client_id)
    )
    db.commit()
    return {"message": "Client mis à jour"}


@app.delete("/api/clients/{client_id}")
def delete_client(client_id: int, db: sqlite3.Connection = Depends(get_db)):
    db.execute("DELETE FROM clients WHERE id = ?", (client_id,))
    db.commit()
    return {"message": "Client supprimé"}


# ── Sessions ─────────────────────────────────────────────────

@app.get("/api/sessions", response_model=List[dict])
def list_sessions(client_id: Optional[int] = None, db: sqlite3.Connection = Depends(get_db)):
    if client_id:
        rows = db.execute(
            "SELECT s.*, c.name as client_name, c.hourly_rate FROM sessions s JOIN clients c ON c.id = s.client_id WHERE s.client_id = ? ORDER BY s.date DESC",
            (client_id,)
        ).fetchall()
    else:
        rows = db.execute(
            "SELECT s.*, c.name as client_name, c.hourly_rate FROM sessions s JOIN clients c ON c.id = s.client_id ORDER BY s.date DESC"
        ).fetchall()
    result = []
    for r in rows:
        d = dict(r)
        d["amount"] = (d["duration_minutes"] / 60.0) * (d["hourly_rate"] or 0) if d["billed"] else 0
        result.append(d)
    return result


@app.post("/api/sessions")
def create_session(session: SessionCreate, db: sqlite3.Connection = Depends(get_db)):
    c = db.execute(
        "INSERT INTO sessions (client_id, date, duration_minutes, notes, billed) VALUES (?,?,?,?,?)",
        (session.client_id, str(session.date), session.duration_minutes, session.notes, int(session.billed))
    )
    db.commit()
    return {"id": c.lastrowid, "message": "Séance ajoutée"}


@app.delete("/api/sessions/{session_id}")
def delete_session(session_id: int, db: sqlite3.Connection = Depends(get_db)):
    db.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
    db.commit()
    return {"message": "Séance supprimée"}


# ── Payments ─────────────────────────────────────────────────

@app.get("/api/payments", response_model=List[dict])
def list_payments(client_id: Optional[int] = None, db: sqlite3.Connection = Depends(get_db)):
    if client_id:
        rows = db.execute(
            "SELECT p.*, c.name as client_name FROM payments p JOIN clients c ON c.id = p.client_id WHERE p.client_id = ? ORDER BY p.date DESC",
            (client_id,)
        ).fetchall()
    else:
        rows = db.execute(
            "SELECT p.*, c.name as client_name FROM payments p JOIN clients c ON c.id = p.client_id ORDER BY p.date DESC"
        ).fetchall()
    return [dict(r) for r in rows]


@app.post("/api/payments")
def create_payment(payment: PaymentCreate, db: sqlite3.Connection = Depends(get_db)):
    c = db.execute(
        "INSERT INTO payments (client_id, date, amount, method, notes) VALUES (?,?,?,?,?)",
        (payment.client_id, str(payment.date), payment.amount, payment.method, payment.notes)
    )
    db.commit()
    return {"id": c.lastrowid, "message": "Paiement enregistré"}


@app.delete("/api/payments/{payment_id}")
def delete_payment(payment_id: int, db: sqlite3.Connection = Depends(get_db)):
    db.execute("DELETE FROM payments WHERE id = ?", (payment_id,))
    db.commit()
    return {"message": "Paiement supprimé"}


# ── Dashboard ────────────────────────────────────────────────

@app.get("/api/dashboard", response_model=DashboardStats)
def dashboard(db: sqlite3.Connection = Depends(get_db)):
    clients = db.execute("SELECT COUNT(*) as n FROM clients").fetchone()["n"]
    sessions = db.execute("SELECT COUNT(*) as n, COALESCE(SUM(duration_minutes),0) as mins FROM sessions").fetchone()
    revenue = db.execute(
        "SELECT COALESCE(SUM(s.duration_minutes / 60.0 * c.hourly_rate), 0) as rev FROM sessions s JOIN clients c ON c.id = s.client_id WHERE s.billed = 1"
    ).fetchone()["rev"]
    paid = db.execute("SELECT COALESCE(SUM(amount), 0) as total FROM payments").fetchone()["total"]

    return DashboardStats(
        total_clients=clients,
        total_sessions=sessions["n"],
        total_hours=round(sessions["mins"] / 60.0, 1),
        total_revenue=round(revenue, 2),
        total_paid=round(paid, 2),
        total_outstanding=round(revenue - paid, 2),
    )
