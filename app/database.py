import sqlite3
from pathlib import Path

import os

DATABASE_PATH = Path(
    os.getenv(
        "DATABASE_PATH",
        str(Path(__file__).parent.parent / "escalas.db")
    )
)

def get_connection():
    conn = sqlite3.connect(str(DATABASE_PATH))
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database with tables"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Create volunteers table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS volunteer (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL UNIQUE,
            ativo BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create roles table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS role (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL UNIQUE
        )
    ''')
    
    # Create volunteer_role junction table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS volunteer_role (
            volunteer_id INTEGER NOT NULL,
            role_id INTEGER NOT NULL,
            PRIMARY KEY (volunteer_id, role_id),
            FOREIGN KEY (volunteer_id) REFERENCES volunteer(id) ON DELETE CASCADE,
            FOREIGN KEY (role_id) REFERENCES role(id) ON DELETE CASCADE
        )
    ''')
    
    # Create schedules table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS schedule (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            week_date TEXT NOT NULL UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create schedule_assignment junction table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS schedule_assignment (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            schedule_id INTEGER NOT NULL,
            volunteer_id INTEGER NOT NULL,
            role_id INTEGER NOT NULL,
            FOREIGN KEY (schedule_id) REFERENCES schedule(id) ON DELETE CASCADE,
            FOREIGN KEY (volunteer_id) REFERENCES volunteer(id) ON DELETE CASCADE,
            FOREIGN KEY (role_id) REFERENCES role(id) ON DELETE CASCADE,
            UNIQUE(schedule_id, volunteer_id, role_id)
        )
    ''')
    
    # Create unavailable table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS volunteer_unavailable (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            volunteer_id INTEGER NOT NULL,
            unavailable_date DATE NOT NULL,
            FOREIGN KEY (volunteer_id) REFERENCES volunteer(id) ON DELETE CASCADE,
            UNIQUE(volunteer_id, unavailable_date)
        )
    ''')
    
    # Insert default roles if not exist
    cursor.execute('SELECT COUNT(*) FROM role')
    if cursor.fetchone()[0] == 0:
        roles = ['MICROFONE', 'SOM', 'INDICADOR']
        for role in roles:
            cursor.execute('INSERT INTO role (nome) VALUES (?)', (role,))
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully!")
