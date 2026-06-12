#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para alterar senha do administrador
"""
from app.database import get_connection
from passlib.context import CryptContext

def alterar_senha():
    # Configurar contexto de senha
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    # Solicitar nova senha
    print("=" * 50)
    print("   ALTERAR SENHA DO ADMINISTRADOR")
    print("=" * 50)
    print()
    
    username = input("Nome de usuário (padrão: admin): ").strip() or "admin"
    nova_senha = input("Digite a nova senha: ").strip()
    confirmar_senha = input("Confirme a nova senha: ").strip()
    
    # Validar senhas
    if nova_senha != confirmar_senha:
        print("\n❌ Erro: As senhas não coincidem!")
        return
    
    if len(nova_senha) < 6:
        print("\n❌ Erro: A senha deve ter pelo menos 6 caracteres!")
        return
    
    # Gerar hash da nova senha
    print("\nProcessando...")
    hashed_password = pwd_context.hash(nova_senha)
    
    # Atualizar no banco de dados
    conn = get_connection()
    cursor = conn.cursor()
    
    # Verificar se usuário existe
    cursor.execute('SELECT id FROM user WHERE username = ?', (username,))
    user = cursor.fetchone()
    
    if not user:
        print(f"\n❌ Erro: Usuário '{username}' não encontrado!")
        conn.close()
        return
    
    # Atualizar senha
    cursor.execute('UPDATE user SET password_hash = ? WHERE username = ?', 
                   (hashed_password, username))
    conn.commit()
    conn.close()
    
    print()
    print("=" * 50)
    print(f"✅ Senha do usuário '{username}' alterada com sucesso!")
    print("=" * 50)
    print("\nVocê já pode fazer login com a nova senha.")
    print()

if __name__ == "__main__":
    try:
        alterar_senha()
    except KeyboardInterrupt:
        print("\n\nOperação cancelada pelo usuário.")
    except Exception as e:
        print(f"\n❌ Erro: {e}")

# Made with Bob
