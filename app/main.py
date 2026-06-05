from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from datetime import datetime, timedelta
from pathlib import Path
import json

from app.database import init_db
from app.models import Volunteer, Schedule
from app.services import (
    VolunteerService, RoleService, ScheduleService, UnavailableService
)

# Initialize database
init_db()

# Create FastAPI app
app = FastAPI(title="Gerenciador de Escalas", version="1.0.0")

# Setup static files and templates
BASE_DIR = Path(__file__).parent
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# Routes

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Dashboard - Current month schedule (all weeks)"""
    weeks = ScheduleService.get_current_month_weeks()
    
    context = {
        "request": request,
        "weeks": weeks
    }
    
    return templates.TemplateResponse("dashboard.html", context)

@app.get("/print-month", response_class=HTMLResponse)
async def print_month(request: Request):
    """Print current month schedule"""
    weeks = ScheduleService.get_current_month_weeks()
    
    if not weeks:
        raise HTTPException(status_code=404, detail="Nenhuma escala para este mês")
    
    context = {
        "request": request,
        "weeks": weeks
    }
    
    return templates.TemplateResponse("print.html", context)

# API Endpoints - Volunteers

@app.get("/api/volunteers")
async def list_volunteers(ativo_only: bool = False):
    """List all volunteers"""
    volunteers = VolunteerService.list_volunteers(ativo_only)
    return [v.to_dict() for v in volunteers]

@app.post("/api/volunteers")
async def create_volunteer(data: dict):
    """Create new volunteer"""
    nome = data.get("nome")
    roles = data.get("roles", [])
    
    if not nome or not roles:
        raise HTTPException(status_code=400, detail="Nome e roles são obrigatórios")
    
    volunteer = VolunteerService.create_volunteer(nome, roles)
    return volunteer.to_dict()

@app.get("/api/volunteers/{volunteer_id}")
async def get_volunteer(volunteer_id: int):
    """Get volunteer by ID"""
    volunteer = VolunteerService.get_volunteer(volunteer_id)
    
    if not volunteer:
        raise HTTPException(status_code=404, detail="Voluntário não encontrado")
    
    return volunteer.to_dict()

@app.put("/api/volunteers/{volunteer_id}")
async def update_volunteer(volunteer_id: int, data: dict):
    """Update volunteer"""
    volunteer = VolunteerService.get_volunteer(volunteer_id)
    
    if not volunteer:
        raise HTTPException(status_code=404, detail="Voluntário não encontrado")
    
    nome = data.get("nome", volunteer.nome)
    roles = data.get("roles", volunteer.roles)
    ativo = data.get("ativo", volunteer.ativo)
    
    VolunteerService.update_volunteer(volunteer_id, nome, roles, ativo)
    updated = VolunteerService.get_volunteer(volunteer_id)
    
    return updated.to_dict()

@app.delete("/api/volunteers/{volunteer_id}")
async def delete_volunteer(volunteer_id: int):
    """Delete volunteer (soft delete - inactivate)"""
    volunteer = VolunteerService.get_volunteer(volunteer_id)
    
    if not volunteer:
        raise HTTPException(status_code=404, detail="Voluntário não encontrado")
    
    VolunteerService.update_volunteer(volunteer_id, volunteer.nome, volunteer.roles, False)
    return {"message": "Voluntário inativado com sucesso"}

# API Endpoints - Roles

@app.get("/api/roles")
async def list_roles():
    """List all roles"""
    roles = RoleService.list_roles()
    return [r.to_dict() for r in roles]

# API Endpoints - Schedules

@app.get("/api/schedules")
async def list_schedules():
    """List all schedules"""
    schedules = ScheduleService.list_schedules()
    return [s.to_dict() for s in schedules]

@app.post("/api/schedules")
async def create_schedule(data: dict):
    """Create new schedule"""
    week_date = data.get("week_date")
    assignments = data.get("assignments", {})
    
    if not week_date:
        raise HTTPException(status_code=400, detail="week_date é obrigatório (formato DD/MM/YYYY)")
    
    # Check if schedule already exists
    existing = ScheduleService.get_schedule_by_date(week_date)
    if existing:
        raise HTTPException(status_code=409, detail="Escala para esta semana já existe")
    
    schedule = ScheduleService.create_schedule(week_date, assignments)
    return schedule.to_dict()

@app.get("/api/schedules/{schedule_id}")
async def get_schedule(schedule_id: int):
    """Get schedule by ID"""
    schedule = ScheduleService.get_schedule(schedule_id)
    
    if not schedule:
        raise HTTPException(status_code=404, detail="Escala não encontrada")
    
    return schedule.to_dict()

@app.put("/api/schedules/{schedule_id}")
async def update_schedule(schedule_id: int, data: dict):
    """Update schedule"""
    schedule = ScheduleService.get_schedule(schedule_id)
    
    if not schedule:
        raise HTTPException(status_code=404, detail="Escala não encontrada")
    
    assignments = data.get("assignments", {})
    ScheduleService.update_schedule(schedule_id, assignments)
    
    updated = ScheduleService.get_schedule(schedule_id)
    return updated.to_dict()

@app.delete("/api/schedules/{schedule_id}")
async def delete_schedule(schedule_id: int):
    """Delete schedule"""
    schedule = ScheduleService.get_schedule(schedule_id)
    
    if not schedule:
        raise HTTPException(status_code=404, detail="Escala não encontrada")
    
    ScheduleService.delete_schedule(schedule_id)
    return {"message": "Escala deletada com sucesso"}

# API Endpoints - Unavailable

@app.post("/api/unavailable")
async def add_unavailable(data: dict):
    """Mark volunteer as unavailable on a date"""
    volunteer_id = data.get("volunteer_id")
    unavailable_date = data.get("unavailable_date")
    
    if not volunteer_id or not unavailable_date:
        raise HTTPException(status_code=400, detail="volunteer_id e unavailable_date são obrigatórios")
    
    UnavailableService.add_unavailable(volunteer_id, unavailable_date)
    return {"message": "Indisponibilidade registrada com sucesso"}

# Web Pages

@app.get("/voluntarios", response_class=HTMLResponse)
async def volunteers_page(request: Request):
    """Volunteers management page"""
    volunteers = VolunteerService.list_volunteers()
    roles = RoleService.list_roles()
    
    return templates.TemplateResponse("voluntarios.html", {
        "request": request,
        "volunteers": [v.to_dict() for v in volunteers],
        "roles": [r.to_dict() for r in roles]
    })

@app.get("/escalas", response_class=HTMLResponse)
async def schedules_page(request: Request):
    """Schedules management page"""
    schedules = ScheduleService.list_schedules()
    volunteers = VolunteerService.list_volunteers(ativo_only=True)
    roles = RoleService.list_roles()
    
    return templates.TemplateResponse("escalas.html", {
        "request": request,
        "schedules": [s.to_dict() for s in schedules],
        "volunteers": [v.to_dict() for v in volunteers],
        "roles": [r.to_dict() for r in roles]
    })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
