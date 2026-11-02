from app.database import get_connection
from app.models import Volunteer, Role, Schedule, ScheduleAssignment
from datetime import datetime, timedelta
from typing import List, Optional
import locale

# Set locale to Portuguese Brazil
try:
    locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')
except:
    try:
        locale.setlocale(locale.LC_TIME, 'Portuguese_Brazil.1252')
    except:
        pass  # Keep default if Portuguese locale not available

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
        # Portuguese month names mapping
        month_names_pt = {
            1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
            5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
            9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
        }
        
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
            
            # Get month name in Portuguese
            month_name = month_names_pt.get(current.month, current.strftime('%B'))
            
            weeks.append({
                'week_date': week_date,
                'week_start': current,
                'week_end': week_end,
                'month_name': month_name,
                'schedule': schedule
            })
            
            current += timedelta(days=7)
        
        return weeks
    
    @staticmethod
    def get_current_and_next_weeks(weeks_ahead: int = 3):
        """Get current week and next N weeks with their schedules
        
        Args:
            weeks_ahead: Number of weeks to show ahead (default: 3)
        
        Returns:
            List of weeks with schedules (current week + weeks_ahead)
        """
        # Portuguese month names mapping
        month_names_pt = {
            1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
            5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
            9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
        }
        
        today = datetime.now()
        
        # Find the Monday of current week (Monday = 0)
        days_since_monday = today.weekday()
        current_week_start = today - timedelta(days=days_since_monday)
        
        weeks = []
        
        # Get current week + next N weeks
        for i in range(weeks_ahead + 1):  # +1 to include current week
            week_start = current_week_start + timedelta(days=7 * i)
            week_date = week_start.strftime('%d/%m/%Y')
            week_end = week_start + timedelta(days=6)
            schedule = ScheduleService.get_schedule_by_date(week_date)
            
            # Get month name in Portuguese
            month_name = month_names_pt.get(week_start.month, week_start.strftime('%B'))
            
            weeks.append({
                'week_date': week_date,
                'week_start': week_start,
                'week_end': week_end,
                'month_name': month_name,
                'schedule': schedule
            })
        
        return weeks
    
    @staticmethod
    def get_weeks_in_range(start_date: str, end_date: str):
        """
        Return weeks between start_date and end_date (both DD/MM/YYYY, inclusive).
        Each week entry matches the format returned by get_current_month_weeks.
        """
        month_names_pt = {
            1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
            5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
            9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
        }

        def parse(d: str):
            day, month, year = d.split('/')
            return datetime(int(year), int(month), int(day))

        start_dt = parse(start_date)
        end_dt = parse(end_date)

        # Snap start to the Monday of that week
        start_dt -= timedelta(days=start_dt.weekday())

        weeks = []
        current = start_dt
        while current <= end_dt:
            week_date = current.strftime('%d/%m/%Y')
            week_end = current + timedelta(days=6)
            schedule = ScheduleService.get_schedule_by_date(week_date)
            month_name = month_names_pt.get(current.month, current.strftime('%B'))
            weeks.append({
                'week_date': week_date,
                'week_start': current,
                'week_end': week_end,
                'month_name': month_name,
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
            INSERT OR IGNORE INTO volunteer_unavailable (volunteer_id, unavailable_date)
            VALUES (?, ?)
        ''', (volunteer_id, unavailable_date))
        
        conn.commit()
        conn.close()
    
    @staticmethod
    def remove_unavailable(volunteer_id: int, unavailable_date: str):
        """Remove unavailable date for volunteer"""
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            DELETE FROM volunteer_unavailable
            WHERE volunteer_id = ? AND unavailable_date = ?
        ''', (volunteer_id, unavailable_date))
        
        conn.commit()
        conn.close()
    
    @staticmethod
    def list_unavailable(volunteer_id: int) -> List[str]:
        """List all unavailable dates for a volunteer"""
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT unavailable_date FROM volunteer_unavailable
            WHERE volunteer_id = ?
            ORDER BY unavailable_date
        ''', (volunteer_id,))
        
        dates = [row[0] for row in cursor.fetchall()]
        conn.close()
        return dates
    
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


class HistoryService:
    @staticmethod
    def get_volunteer_stats() -> List[dict]:
        """Return participation count per volunteer per role across all schedules"""
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT v.id, v.nome, r.nome as role_nome, COUNT(sa.id) as total
            FROM volunteer v
            LEFT JOIN schedule_assignment sa ON v.id = sa.volunteer_id
            LEFT JOIN role r ON sa.role_id = r.id
            WHERE v.ativo = 1
            GROUP BY v.id, r.nome
            ORDER BY v.nome, r.nome
        ''')
        
        rows = cursor.fetchall()
        conn.close()
        
        # Aggregate per volunteer
        volunteers: dict = {}
        for row in rows:
            vid, vname, role, total = row[0], row[1], row[2], row[3]
            if vid not in volunteers:
                volunteers[vid] = {'id': vid, 'nome': vname, 'total': 0, 'roles': {}}
            if role:
                volunteers[vid]['roles'][role] = total
                volunteers[vid]['total'] += total
        
        return sorted(volunteers.values(), key=lambda x: x['total'], reverse=True)

    @staticmethod
    def get_recent_schedules(limit: int = 10) -> List[dict]:
        """Return recent schedules with assignment details"""
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT s.id, s.week_date, s.created_at
            FROM schedule s
            ORDER BY s.week_date DESC
            LIMIT ?
        ''', (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        schedules = []
        for row in rows:
            s = ScheduleService.get_schedule(row[0])
            schedules.append({
                'id': row[0],
                'week_date': row[1],
                'created_at': row[2],
                'assignments': [a.to_dict() for a in s.assignments] if s else []
            })
        return schedules


class AutoScheduleService:

    @staticmethod
    def _get_assignment_counts(role_name: str) -> dict:
        """Return {volunteer_id: total_count} of past assignments for a role."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT sa.volunteer_id, COUNT(sa.id) as cnt
            FROM schedule_assignment sa
            JOIN role r ON sa.role_id = r.id
            WHERE r.nome = ?
            GROUP BY sa.volunteer_id
        ''', (role_name,))
        counts = {row[0]: row[1] for row in cursor.fetchall()}
        conn.close()
        return counts

    @staticmethod
    def _get_prev_week_ids_for_roles(week_date: str, role_names: List[str]) -> set:
        """
        Return volunteer IDs who served in ANY of the given roles in the
        immediately preceding week (week_date - 7 days).
        """
        day, month, year = week_date.split('/')
        week_dt = datetime(int(year), int(month), int(day))
        prev_date = (week_dt - timedelta(days=7)).strftime('%d/%m/%Y')

        conn = get_connection()
        cursor = conn.cursor()
        placeholders = ','.join('?' for _ in role_names)
        cursor.execute(f'''
            SELECT sa.volunteer_id
            FROM schedule_assignment sa
            JOIN schedule s ON sa.schedule_id = s.id
            JOIN role r ON sa.role_id = r.id
            WHERE s.week_date = ? AND r.nome IN ({placeholders})
        ''', [prev_date] + role_names)
        ids = {row[0] for row in cursor.fetchall()}
        conn.close()
        return ids

    @staticmethod
    def _pick(role_name: str, count_needed: int, week_iso: str, week_date: str,
              global_exclude: set, prev_week_penalty: set) -> List:
        """
        Pick `count_needed` volunteers for `role_name`.

        global_exclude  – IDs already assigned to ANY role this week (never reuse).
        prev_week_penalty – IDs who served in this role-group last week (deprioritise).

        Sort key: (served_last_week, total_historical_count, name)
        Raises ValueError if pool is insufficient.
        """
        volunteers = VolunteerService.list_volunteers(ativo_only=True)
        eligible = [v for v in volunteers if role_name in v.roles]

        if not eligible:
            raise ValueError(f"Nenhum voluntário ativo com a função {role_name}")

        available = [
            v for v in eligible
            if UnavailableService.is_available(v.id, week_iso)
            and v.id not in global_exclude
        ]

        if len(available) < count_needed:
            raise ValueError(
                f"Voluntários insuficientes para {role_name} "
                f"(necessário: {count_needed}, disponível: {len(available)})"
            )

        counts = AutoScheduleService._get_assignment_counts(role_name)

        def sort_key(v):
            penalised = 1 if v.id in prev_week_penalty else 0
            return (penalised, counts.get(v.id, 0), v.nome)

        return sorted(available, key=sort_key)[:count_needed]

    @staticmethod
    def generate(week_date: str) -> dict:
        """
        Generate schedule assignments with full intelligence rules:

        1. A volunteer can only appear in ONE role per week (no duplicates).
        2. Nobody repeats in the same role in consecutive weeks (back-to-back penalty).
        3. Indicadores (Entrada + Auditório) are treated as the SAME group:
           - The two slots must be filled by different people.
           - Anyone who was an indicador (either position) last week is deprioritised
             for BOTH indicador slots this week.
        4. Fair rotation: least-assigned volunteer per role goes first.
        5. Unavailable volunteers are skipped.

        week_date: DD/MM/YYYY
        Returns {role: [volunteer_ids]} or raises ValueError.
        """
        day, month, year = week_date.split('/')
        week_dt = datetime(int(year), int(month), int(day))
        week_iso = week_dt.strftime('%Y-%m-%d')

        # IDs assigned to any role this week — grows as we assign each role
        global_used: set = set()

        result = {}

        # --- MICROFONE (2 people) ---
        # Previous-week penalty: only who did MICROFONE last week
        prev_mic = AutoScheduleService._get_prev_week_ids_for_roles(week_date, ['MICROFONE'])
        mic = AutoScheduleService._pick('MICROFONE', 2, week_iso, week_date,
                                        global_exclude=global_used,
                                        prev_week_penalty=prev_mic)
        result['MICROFONE'] = [v.id for v in mic]
        global_used.update(result['MICROFONE'])

        # --- SOM (1 person) ---
        prev_som = AutoScheduleService._get_prev_week_ids_for_roles(week_date, ['SOM'])
        som = AutoScheduleService._pick('SOM', 1, week_iso, week_date,
                                        global_exclude=global_used,
                                        prev_week_penalty=prev_som)
        result['SOM'] = [v.id for v in som]
        global_used.update(result['SOM'])

        # --- INDICADORES (treated as one group for back-to-back rule) ---
        # Anyone who was any indicador last week is penalised for both slots
        prev_ind = AutoScheduleService._get_prev_week_ids_for_roles(
            week_date, ['INDICADOR_ENTRADA', 'INDICADOR_AUDITORIO']
        )

        # Entrada — picks from global pool (already excludes mic + som people)
        entrada = AutoScheduleService._pick('INDICADOR_ENTRADA', 1, week_iso, week_date,
                                            global_exclude=global_used,
                                            prev_week_penalty=prev_ind)
        result['INDICADOR_ENTRADA'] = [v.id for v in entrada]
        global_used.update(result['INDICADOR_ENTRADA'])  # block from Auditório slot

        # Auditório — global_used now also contains the Entrada person
        auditorio = AutoScheduleService._pick('INDICADOR_AUDITORIO', 1, week_iso, week_date,
                                              global_exclude=global_used,
                                              prev_week_penalty=prev_ind)
        result['INDICADOR_AUDITORIO'] = [v.id for v in auditorio]

        return result
