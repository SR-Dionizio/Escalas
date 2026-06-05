```mermaid
graph TB
    subgraph Frontend["🖥️ Frontend (Browser)"]
        Dashboard["📅 Dashboard"]
        Voluntarios["👥 Voluntários"]
        Escalas["📋 Escalas"]
        Print["🖨️ Impressão"]
    end
    
    subgraph Backend["⚙️ Backend (FastAPI)"]
        Main["main.py<br/>FastAPI App"]
        VolService["VolunteerService"]
        RoleService["RoleService"]
        SchedService["ScheduleService"]
    end
    
    subgraph Database["💾 Database (SQLite)"]
        VolTable["volunteer"]
        RoleTable["role"]
        VolRoleTable["volunteer_role"]
        SchedTable["schedule"]
        AssignTable["schedule_assignment"]
        UnavailTable["volunteer_unavailable"]
    end
    
    subgraph Routes["🛣️ API Routes"]
        VolAPI["/api/volunteers"]
        RoleAPI["/api/roles"]
        SchedAPI["/api/schedules"]
        UnavailAPI["/api/unavailable"]
    end
    
    Dashboard -->|GET /| Main
    Voluntarios -->|GET /voluntarios| Main
    Escalas -->|GET /escalas| Main
    Print -->|GET /print-week| Main
    
    Main -->|CRUD| VolAPI
    Main -->|READ| RoleAPI
    Main -->|CRUD| SchedAPI
    Main -->|POST| UnavailAPI
    
    VolAPI -->|Calls| VolService
    RoleAPI -->|Calls| RoleService
    SchedAPI -->|Calls| SchedService
    UnavailAPI -->|Calls| VolService
    
    VolService -->|Query/Insert| VolTable
    VolService -->|Query/Insert| VolRoleTable
    VolService -->|Query/Insert| UnavailTable
    
    RoleService -->|Query| RoleTable
    
    SchedService -->|Query/Insert| SchedTable
    SchedService -->|Query/Insert| AssignTable
    SchedService -->|Query| VolTable
    SchedService -->|Query| RoleTable
    
    Main -->|Render| Dashboard
    Main -->|Render| Voluntarios
    Main -->|Render| Escalas
    Main -->|Render| Print
```

## Architecture Overview

### Layers

1. **Presentation Layer** (Frontend)
   - HTML templates with Jinja2
   - Bootstrap 5 styling
   - JavaScript for interactivity

2. **API Layer** (Routes)
   - RESTful endpoints
   - FastAPI automatic docs at /docs

3. **Business Logic** (Services)
   - VolunteerService
   - RoleService
   - ScheduleService
   - UnavailableService

4. **Data Access Layer** (Database)
   - SQLite connection management
   - CRUD operations
   - Relationship management

### Data Flow Example: Creating a Schedule

```
User clicks "New Schedule"
        ↓
Fill form and submit
        ↓
POST /api/schedules with assignments
        ↓
FastAPI validates and routes to handler
        ↓
ScheduleService.create_schedule() called
        ↓
Insert into schedule table → get schedule_id
        ↓
For each volunteer in assignments:
  - Insert into schedule_assignment table
        ↓
Commit transaction
        ↓
Return created schedule with ID
        ↓
JavaScript updates UI table
        ↓
Success message shown to user
```

### Request/Response Flow

```
Browser HTTP Request
        ↓
FastAPI Router
        ↓
Service Method
        ↓
Database Query
        ↓
Result → JSON
        ↓
FastAPI Response
        ↓
Browser renders/updates
```

### Database Relationships

```
Volunteer (1) ----→ (N) Volunteer_Role ----→ (1) Role
    ↓
    └→ Volunteer_Unavailable
    
Schedule (1) ----→ (N) Schedule_Assignment ----→ (1) Volunteer
                          ↓
                          └→ Role
```

### Technologies Stack

```
┌─────────────────────────────────────┐
│        Client (Browser)             │
│  HTML5 | CSS3 | JavaScript          │
│  Bootstrap 5 Framework              │
└─────────────────────────────────────┘
              ↓ HTTP
┌─────────────────────────────────────┐
│      FastAPI Web Framework          │
│  - Automatic API documentation      │
│  - Type validation (Pydantic)       │
│  - CORS support                     │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│       Uvicorn ASGI Server           │
│  Async request handling             │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│        SQLite Database              │
│  - Local file based                 │
│  - ACID transactions                │
│  - Perfect for small deployments    │
└─────────────────────────────────────┘
```

### Deployment Options

```
┌────────────┐
│ Laptop/PC  │ → Direct run with Python
└────────────┘

┌────────────┐
│ Raspberry  │ → Python + Gunicorn + systemd
│ Pi         │
└────────────┘

┌────────────┐
│ Docker     │ → Container deployment
│ Container  │
└────────────┘

┌────────────┐
│ VPS/Cloud  │ → Gunicorn + Nginx reverse proxy
│            │
└────────────┘
```
