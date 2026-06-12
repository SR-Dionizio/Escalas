# -*- coding: utf-8 -*-
"""
Script de migração para separar INDICADOR em INDICADOR_ENTRADA e INDICADOR_AUDITORIO
"""
import sqlite3
from pathlib import Path
import os

DATABASE_PATH = Path(
    os.getenv(
        "DATABASE_PATH",
        str(Path(__file__).parent / "escalas.db")
    )
)

def migrate():
    conn = sqlite3.connect(str(DATABASE_PATH))
    cursor = conn.cursor()
    
    print("Iniciando migração...")
    
    # 1. Verificar se as novas roles já existem
    cursor.execute("SELECT nome FROM role WHERE nome IN ('INDICADOR_ENTRADA', 'INDICADOR_AUDITORIO')")
    existing = cursor.fetchall()
    
    if len(existing) == 2:
        print("[OK] Migracao ja foi executada anteriormente")
        conn.close()
        return
    
    # 2. Adicionar as novas roles
    print("Adicionando novas funções...")
    cursor.execute("INSERT OR IGNORE INTO role (nome) VALUES ('INDICADOR_ENTRADA')")
    cursor.execute("INSERT OR IGNORE INTO role (nome) VALUES ('INDICADOR_AUDITORIO')")
    
    # 3. Obter IDs das roles
    cursor.execute("SELECT id FROM role WHERE nome = 'INDICADOR'")
    old_indicador_id = cursor.fetchone()
    
    cursor.execute("SELECT id FROM role WHERE nome = 'INDICADOR_ENTRADA'")
    entrada_id = cursor.fetchone()[0]
    
    cursor.execute("SELECT id FROM role WHERE nome = 'INDICADOR_AUDITORIO'")
    auditorio_id = cursor.fetchone()[0]
    
    if old_indicador_id:
        old_indicador_id = old_indicador_id[0]
        
        # 4. Migrar volunteer_role: voluntários que tinham INDICADOR agora têm ambos
        print("Migrando voluntários...")
        cursor.execute("SELECT volunteer_id FROM volunteer_role WHERE role_id = ?", (old_indicador_id,))
        volunteers = cursor.fetchall()
        
        for (volunteer_id,) in volunteers:
            cursor.execute("INSERT OR IGNORE INTO volunteer_role (volunteer_id, role_id) VALUES (?, ?)",
                         (volunteer_id, entrada_id))
            cursor.execute("INSERT OR IGNORE INTO volunteer_role (volunteer_id, role_id) VALUES (?, ?)",
                         (volunteer_id, auditorio_id))
        
        print(f"[OK] {len(volunteers)} voluntarios migrados")
        
        # 5. Migrar schedule_assignment: distribuir indicadores existentes
        print("Migrando escalas...")
        cursor.execute("""
            SELECT schedule_id, volunteer_id, id 
            FROM schedule_assignment 
            WHERE role_id = ?
            ORDER BY schedule_id, id
        """, (old_indicador_id,))
        assignments = cursor.fetchall()
        
        # Agrupar por schedule_id
        schedules = {}
        for schedule_id, volunteer_id, assignment_id in assignments:
            if schedule_id not in schedules:
                schedules[schedule_id] = []
            schedules[schedule_id].append((volunteer_id, assignment_id))
        
        # Para cada escala, atribuir o primeiro como ENTRADA e o segundo como AUDITORIO
        for schedule_id, volunteers_list in schedules.items():
            if len(volunteers_list) >= 1:
                # Primeiro indicador vira ENTRADA
                cursor.execute("UPDATE schedule_assignment SET role_id = ? WHERE id = ?",
                             (entrada_id, volunteers_list[0][1]))
            if len(volunteers_list) >= 2:
                # Segundo indicador vira AUDITORIO
                cursor.execute("UPDATE schedule_assignment SET role_id = ? WHERE id = ?",
                             (auditorio_id, volunteers_list[1][1]))
        
        print(f"[OK] {len(schedules)} escalas migradas")
        
        # 6. Remover a role antiga INDICADOR
        print("Removendo função antiga...")
        cursor.execute("DELETE FROM volunteer_role WHERE role_id = ?", (old_indicador_id,))
        cursor.execute("DELETE FROM role WHERE id = ?", (old_indicador_id,))
    
    conn.commit()
    conn.close()
    
    print("\n[SUCESSO] Migracao concluida com sucesso!")
    print("As funcoes agora sao:")
    print("  - MICROFONE")
    print("  - SOM")
    print("  - INDICADOR_ENTRADA")
    print("  - INDICADOR_AUDITORIO")

if __name__ == "__main__":
    migrate()

# Made with Bob
