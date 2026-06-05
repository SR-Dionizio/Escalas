from app.database import get_connection
from app.models import Volunteer, Role, Schedule, ScheduleAssignment
from datetime import datetime, timedelta
from typing import List, Optional

class VolunteerService:
    @staticmethod
    def create_volunteer(nome: str, roles: List[str]) -> Volunteer:
        """Create a new volunteer"""
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('INSERT INTO volunteer (nome, ativo) VALUES (?, ?)', (nome, 1))
        volunteer_id = cursor.lastrowid
        
        # Add roles
        for role in roles:
            cursor.execute('SELECT id FROM role WHERE nome = ?', (role,))
            role_id = cursor.fetchone()[0]
            cursor.execute('INSERT INTO volunteer_role (volunteer_id, role_id) VALUES (?, ?)',
                         (volunteer_id, role_id))
        
        conn.commit()
        conn.close()
        
        return VolunteerService.get_volunteer(volunteer_id)
    
    @staticmethod
    def get_volunteer(volunteer_id: int) -> Optional[Volunteer]:
        """Get volunteer by ID"""
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT id, nome, ativo FROM volunteer WHERE id = ?', (volunteer_id,))
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            return None
        
        # Get roles
        cursor.execute('''
            SELECT r.nome FROM role r
            JOIN volunteer_role vr ON r.id = vr.role_id
            WHERE vr.volunteer_id = ?
        ''', (volunteer_id,))
        roles = [r[0] for r in cursor.fetchall()]
        
        conn.close()
        
        volunteer = Volunteer(row[0], row[1], row[2], roles)
        return volunteer
    
    @staticmethod
    def list_volunteers(ativo_only: bool = False) -> List[Volunteer]:
        """List all volunteers"""
        conn = get_connection()
        cursor = conn.cursor()
        
        if ativo_only:
            cursor.execute('SELECT id FROM volunteer WHERE ativo = 1')
        else:
            cursor.execute('SELECT id FROM volunteer')
        
        volunteers = []
        for row in cursor.fetchall():
            volunteer = VolunteerService.get_volunteer(row[0])
            if volunteer:
                volunteers.append(volunteer)
        
        conn.close()
        return volunteers
    
    @staticmethod
    def update_volunteer(volunteer_id: int, nome: str, roles: List[str], ativo: bool):
        """Update volunteer"""
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('UPDATE volunteer SET nome = ?, ativo = ? WHERE id = ?',
                      (nome, ativo, volunteer_id))
        
        # Remove old roles
        cursor.execute('DELETE FROM volunteer_role WHERE volunteer_id = ?', (volunteer_id,))
        
        # Add new roles
        for role in roles:
            cursor.execute('SELECT id FROM role WHERE nome = ?', (role,))
            role_id = cursor.fetchone()[0]
            cursor.execute('INSERT INTO volunteer_role (volunteer_id, role_id) VALUES (?, ?)',
                         (volunteer_id, role_id))
        
        conn.commit()
        conn.close()
    
    @staticmethod
    def delete_volunteer(volunteer_id: int):
        """Delete volunteer"""
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM volunteer WHERE id = ?', (volunteer_id,))
        conn.commit()
        conn.close()

class RoleService:
    @staticmethod
    def list_roles() -> List[Role]:
        """List all roles"""
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT id, nome FROM role ORDER BY nome')
        roles = [Role(row[0], row[1]) for row in cursor.fetchall()]
        
        conn.close()
        return roles

class ScheduleService:
    @staticmethod
    def create_schedule(week_date: str, assignments: dict) -> Schedule:
        """
        Create a new schedule
        week_date: Format DD/MM/YYYY (first day of week)
        assignments: {role_name: [volunteer_ids]}
        """
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('INSERT INTO schedule (week_date) VALUES (?)', (week_date,))
        schedule_id = cursor.lastrowid
        
        # Add assignments
        for role_name, volunteer_ids in assignments.items():
            cursor.execute('SELECT id FROM role WHERE nome = ?', (role_name,))
            role_id = cursor.fetchone()[0]
            
            for volunteer_id in volunteer_ids:
                cursor.execute('''
                    INSERT INTO schedule_assignment (schedule_id, volunteer_id, role_id)
                    VALUES (?, ?, ?)
                ''', (schedule_id, volunteer_id, role_id))
        
        conn.commit()
        conn.close()
        
        return ScheduleService.get_schedule(schedule_id)
    
    @staticmethod
    def get_schedule(schedule_id: int) -> Optional[Schedule]:
        """Get schedule by ID"""
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT id, week_date FROM schedule WHERE id = ?', (schedule_id,))
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            return None
        
        # Get assignments
        cursor.execute('''
            SELECT sa.id, sa.schedule_id, sa.volunteer_id, sa.role_id, v.nome, r.nome
            FROM schedule_assignment sa
            JOIN volunteer v ON sa.volunteer_id = v.id
            JOIN role r ON sa.role_id = r.id
            WHERE sa.schedule_id = ?
            ORDER BY r.nome
        ''', (schedule_id,))
        
        assignments = [ScheduleAssignment(a[0], a[1], a[2], a[3], a[4], a[5]) for a in cursor.fetchall()]
        
        conn.close()
        
        schedule = Schedule(row[0], row[1], assignments)
        return schedule
    
    @staticmethod
    def get_schedule_by_date(week_date: str) -> Optional[Schedule]:
        """Get schedule by week (DD/MM/YYYY format)"""
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT id FROM schedule WHERE week_date = ?', (week_date,))
        row = cursor.fetchone()
        
        conn.close()
        
        if not row:
            return None
        
        return ScheduleService.get_schedule(row[0])
    
    @staticmethod
    def get_current_month_weeks():
        """Get all weeks of current month with their schedules"""
        today = datetime.now()
        year = today.year
        month = today.month
        
        # Find first day of month
        first_day = datetime(year, month, 1)
        # Find first Monday on or before first day (Monday = 0)
        days_since_monday = first_day.weekday()
        week_start = first_day - timedelta(days=days_since_monday)
        
        weeks = []
        current = week_start
        
        # Iterate through all weeks that include days from this month
        while current.month <= month or (current.day <= 7 and current.month == month + 1 and month < 12):
            if current.month > month and current.day > 6:
                break
            
            week_date = current.strftime('%d/%m/%Y')
            week_end = current + timedelta(days=6)
            schedule = ScheduleService.get_schedule_by_date(week_date)
            
            weeks.append({
                'week_date': week_date,
                'week_start': current,
                'week_end': week_end,
                'schedule': schedule
            })
            
            current += timedelta(days=7)
        
        return weeks
    
    @staticmethod
    def list_schedules() -> List[Schedule]:
        """List all schedules"""
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT id FROM schedule ORDER BY week_date DESC')
        schedules = [ScheduleService.get_schedule(row[0]) for row in cursor.fetchall()]
        
        conn.close()
        return schedules
    
    @staticmethod
    def update_schedule(schedule_id: int, assignments: dict):
        """Update schedule assignments"""
        conn = get_connection()
        cursor = conn.cursor()
        
        # Delete old assignments
        cursor.execute('DELETE FROM schedule_assignment WHERE schedule_id = ?', (schedule_id,))
        
        # Add new assignments
        for role_name, volunteer_ids in assignments.items():
            cursor.execute('SELECT id FROM role WHERE nome = ?', (role_name,))
            role_id = cursor.fetchone()[0]
            
            for volunteer_id in volunteer_ids:
                cursor.execute('''
                    INSERT INTO schedule_assignment (schedule_id, volunteer_id, role_id)
                    VALUES (?, ?, ?)
                ''', (schedule_id, volunteer_id, role_id))
        
        conn.commit()
        conn.close()
    
    @staticmethod
    def delete_schedule(schedule_id: int):
        """Delete schedule"""
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM schedule WHERE id = ?', (schedule_id,))
        conn.commit()
        conn.close()

class UnavailableService:
    @staticmethod
    def add_unavailable(volunteer_id: int, unavailable_date: str):
        """Add unavailable date for volunteer"""
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO volunteer_unavailable (volunteer_id, unavailable_date)
            VALUES (?, ?)
        ''', (volunteer_id, unavailable_date))
        
        conn.commit()
        conn.close()
    
    @staticmethod
    def is_available(volunteer_id: int, check_date: str) -> bool:
        """Check if volunteer is available on date"""
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT COUNT(*) FROM volunteer_unavailable
            WHERE volunteer_id = ? AND unavailable_date = ?
        ''', (volunteer_id, check_date))
        
        count = cursor.fetchone()[0]
        conn.close()
        
        return count == 0
