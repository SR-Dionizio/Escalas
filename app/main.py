from fastapi import FastAPI, HTTPException, Request, Form, Depends
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from datetime import datetime, timedelta
from pathlib import Path
import json

from app.database import init_db, get_connection
from app.models import Volunteer, Schedule
from app.services import (
    VolunteerService, RoleService, ScheduleService, UnavailableService
)
from app.auth import (
    verify_password, create_access_token, require_auth,
    is_authenticated, get_current_user
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
    """Dashboard - Current month schedule (all weeks) - PUBLIC"""
    weeks = ScheduleService.get_current_month_weeks()
    user = get_current_user(request)
    
    context = {
        "request": request,
        "weeks": weeks,
        "user": user
    }
    
    return templates.TemplateResponse("dashboard.html", context)

@app.get("/print-month", response_class=HTMLResponse)
async def print_month(request: Request):
    """Print current month schedule - PUBLIC"""
    weeks = ScheduleService.get_current_month_weeks()
    
    if not weeks:
        raise HTTPException(status_code=404, detail="Nenhuma escala para este mês")
    
    context = {
        "request": request,
        "weeks": weeks
    }
    
    return templates.TemplateResponse("print.html", context)

# Authentication Routes

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Login page"""
    # If already logged in, redirect to dashboard
    if is_authenticated(request):
        return RedirectResponse(url="/", status_code=302)
    
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    """Process login"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT username, password_hash FROM user WHERE username = ?', (username,))
    user = cursor.fetchone()
    conn.close()
    
    if not user or not verify_password(password, user[1]):
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "Usuário ou senha incorretos"
        })
    
    # Create access token
    access_token = create_access_token(data={"sub": username})
    
    # Redirect to dashboard with cookie
    response = RedirectResponse(url="/", status_code=302)
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=60 * 60 * 24,  # 24 hours
        samesite="lax"
    )
    return response

@app.get("/logout")
async def logout():
    """Logout user"""
    response = RedirectResponse(url="/", status_code=302)
    response.delete_cookie("access_token")
    return response

@app.get("/alterar-senha", response_class=HTMLResponse)
async def change_password_page(request: Request):
    """Change password page - PROTECTED"""
    user = require_auth(request)
    return templates.TemplateResponse("alterar_senha.html", {
        "request": request,
        "user": user
    })

@app.post("/alterar-senha")
async def change_password(
    request: Request,
    current_password: str = Form(...),
    new_password: str = Form(...),
    confirm_password: str = Form(...)
):
    """Process password change - PROTECTED"""
    user = require_auth(request)
    
    # Validate new passwords match
    if new_password != confirm_password:
        return templates.TemplateResponse("alterar_senha.html", {
            "request": request,
            "user": user,
            "error": "As senhas não coincidem!"
        })
    
    # Validate password length
    if len(new_password) < 6:
        return templates.TemplateResponse("alterar_senha.html", {
            "request": request,
            "user": user,
            "error": "A senha deve ter pelo menos 6 caracteres!"
        })
    
    # Get user from database
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT password_hash FROM user WHERE username = ?', (user,))
    user_data = cursor.fetchone()
    
    if not user_data:
        conn.close()
        return templates.TemplateResponse("alterar_senha.html", {
            "request": request,
            "user": user,
            "error": "Usuário não encontrado!"
        })
    
    # Verify current password
    if not verify_password(current_password, user_data[0]):
        conn.close()
        return templates.TemplateResponse("alterar_senha.html", {
            "request": request,
            "user": user,
            "error": "Senha atual incorreta!"
        })
    
    # Update password
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    new_hash = pwd_context.hash(new_password)
    
    cursor.execute('UPDATE user SET password_hash = ? WHERE username = ?',
                   (new_hash, user))
    conn.commit()
    conn.close()
    
    return templates.TemplateResponse("alterar_senha.html", {
        "request": request,
        "user": user,
        "success": "Senha alterada com sucesso!"
    })

# API Endpoints - Volunteers

@app.get("/api/volunteers")
async def list_volunteers(ativo_only: bool = False):
    """List all volunteers"""
    volunteers = VolunteerService.list_volunteers(ativo_only)
    return [v.to_dict() for v in volunteers]

@app.post("/api/volunteers")
async def create_volunteer(request: Request, data: dict):
    """Create new volunteer - PROTECTED"""
    require_auth(request)
    
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
async def update_volunteer(request: Request, volunteer_id: int, data: dict):
    """Update volunteer - PROTECTED"""
    require_auth(request)
    
    volunteer = VolunteerService.get_volunteer(volunteer_id)
    
    if not volunteer:
        raise HTTPException(status_code=404, detail="Voluntário não encontrado")
    
    nome = data.get("nome", volunteer.nome)
    roles = data.get("roles", volunteer.roles)
    ativo = data.get("ativo", volunteer.ativo)
    
    VolunteerService.update_volunteer(volunteer_id, nome, roles, ativo)
    updated = VolunteerService.get_volunteer(volunteer_id)
    
    if not updated:
        raise HTTPException(status_code=500, detail="Erro ao atualizar voluntário")
    
    return updated.to_dict()

@app.delete("/api/volunteers/{volunteer_id}")
async def delete_volunteer(request: Request, volunteer_id: int):
    """Delete volunteer (soft delete - inactivate) - PROTECTED"""
    require_auth(request)
    
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
async def create_schedule(request: Request, data: dict):
    """Create new schedule - PROTECTED"""
    require_auth(request)
    
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
async def update_schedule(request: Request, schedule_id: int, data: dict):
    """Update schedule - PROTECTED"""
    require_auth(request)
    
    schedule = ScheduleService.get_schedule(schedule_id)
    
    if not schedule:
        raise HTTPException(status_code=404, detail="Escala não encontrada")
    
    assignments = data.get("assignments", {})
    ScheduleService.update_schedule(schedule_id, assignments)
    
    updated = ScheduleService.get_schedule(schedule_id)
    if not updated:
        raise HTTPException(status_code=500, detail="Erro ao atualizar escala")
    
    return updated.to_dict()

@app.delete("/api/schedules/{schedule_id}")
async def delete_schedule(request: Request, schedule_id: int):
    """Delete schedule - PROTECTED"""
    require_auth(request)
    
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
    """Volunteers management page - PROTECTED"""
    user = require_auth(request)
    
    volunteers = VolunteerService.list_volunteers()
    roles = RoleService.list_roles()
    
    return templates.TemplateResponse("voluntarios.html", {
        "request": request,
        "volunteers": [v.to_dict() for v in volunteers],
        "roles": [r.to_dict() for r in roles],
        "user": user
    })

@app.get("/escalas", response_class=HTMLResponse)
async def schedules_page(request: Request):
    """Schedules management page - PROTECTED"""
    user = require_auth(request)
    
    schedules = ScheduleService.list_schedules()
    volunteers = VolunteerService.list_volunteers(ativo_only=True)
    roles = RoleService.list_roles()
    
    return templates.TemplateResponse("escalas.html", {
        "request": request,
        "schedules": [s.to_dict() for s in schedules],
        "volunteers": [v.to_dict() for v in volunteers],
        "roles": [r.to_dict() for r in roles],
        "user": user
    })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
