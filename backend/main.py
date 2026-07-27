from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import sqlite3
from pathlib import Path

# Fix de Ruta: Obtener la ruta absoluta exacta de la carpeta donde vive main.py
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "database.db"

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite peticiones desde cualquier origen (Vercel)
    allow_credentials=True,
    allow_methods=["*"],  # Permite GET, POST, PUT, DELETE, etc.
    allow_headers=["*"],
)

app = FastAPI(
    title="API ServiceDesk TI - Empresa Demo",
    description="API REST para la gestión interna de tickets y requerimientos de soporte.",
    version="1.0.0"
)

# Permitir que el Frontend (HTML/JS) se conecte con el Backend (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializar Base de Datos con la ruta absoluta
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            descripcion TEXT NOT NULL,
            prioridad TEXT DEFAULT 'MEDIA',
            estado TEXT DEFAULT 'ABIERTO'
        )
    """)
    conn.commit()
    conn.close()

init_db()

# Modelos Pydantic (Esquema de datos)
class TicketCreate(BaseModel):
    titulo: str
    descripcion: str
    prioridad: Optional[str] = "MEDIA"

class TicketUpdateStatus(BaseModel):
    estado: str

# --- ENDPOINTS REST ---

@app.get("/api/tickets", tags=["Tickets"])
def obtener_tickets():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, titulo, descripcion, prioridad, estado FROM tickets")
    filas = cursor.fetchall()
    conn.close()
    
    return [
        {"id": f[0], "titulo": f[1], "descripcion": f[2], "prioridad": f[3], "estado": f[4]}
        for f in filas
    ]

@app.post("/api/tickets", tags=["Tickets"])
def crear_ticket(ticket: TicketCreate):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO tickets (titulo, descripcion, prioridad) VALUES (?, ?, ?)",
        (ticket.titulo, ticket.descripcion, ticket.prioridad)
    )
    conn.commit()
    nuevo_id = cursor.lastrowid
    conn.close()
    
    return {"mensaje": "Ticket levantado exitosamente", "id": nuevo_id}

@app.put("/api/tickets/{ticket_id}/estado", tags=["Tickets"])
def actualizar_estado(ticket_id: int, payload: TicketUpdateStatus):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE tickets SET estado = ? WHERE id = ?",
        (payload.estado, ticket_id)
    )
    conn.commit()
    filas_afectadas = cursor.rowcount
    conn.close()
    
    if filas_afectadas == 0:
        raise HTTPException(status_code=404, detail="Ticket no encontrado")
        
    return {"mensaje": f"Estado del ticket #{ticket_id} actualizado a {payload.estado}"}

@app.delete("/api/tickets/{ticket_id}", tags=["Tickets"])
def eliminar_ticket(ticket_id: int):
    """Elimina o archiva un ticket de la base de datos."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tickets WHERE id = ?", (ticket_id,))
    conn.commit()
    filas_afectadas = cursor.rowcount
    conn.close()
    
    if filas_afectadas == 0:
        raise HTTPException(status_code=404, detail="Ticket no encontrado")
        
    return {"mensaje": f"Ticket #{ticket_id} eliminado con éxito"}