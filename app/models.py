from datetime import datetime
from typing import List, Optional

class Volunteer:
    def __init__(self, id: int = None, nome: str = None, ativo: bool = True, roles: List[str] = None):
        self.id = id
        self.nome = nome
        self.ativo = ativo
        self.roles = roles or []
    
    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'ativo': self.ativo,
            'roles': self.roles
        }

class Role:
    def __init__(self, id: int = None, nome: str = None):
        self.id = id
        self.nome = nome
    
    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome
        }

class Schedule:
    def __init__(self, id: int = None, week_date: str = None, assignments: List = None):
        self.id = id
        self.week_date = week_date
        self.assignments = assignments or []
    
    def to_dict(self):
        return {
            'id': self.id,
            'week_date': self.week_date,
            'assignments': self.assignments
        }

class ScheduleAssignment:
    def __init__(self, id: int = None, schedule_id: int = None, volunteer_id: int = None, 
                 role_id: int = None, volunteer_name: str = None, role_name: str = None):
        self.id = id
        self.schedule_id = schedule_id
        self.volunteer_id = volunteer_id
        self.role_id = role_id
        self.volunteer_name = volunteer_name
        self.role_name = role_name
    
    def to_dict(self):
        return {
            'id': self.id,
            'schedule_id': self.schedule_id,
            'volunteer_id': self.volunteer_id,
            'role_id': self.role_id,
            'volunteer_name': self.volunteer_name,
            'role_name': self.role_name
        }
