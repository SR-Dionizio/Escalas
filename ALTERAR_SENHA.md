# Como Alterar a Senha do Administrador

## Método 1: Via Script Python (Recomendado)

### Passo 1: Criar o script

Crie um arquivo chamado `alterar_senha.py` na raiz do projeto:

```python
from app.database import get_connection
from passlib.context import CryptContext

def alterar_senha():
    # Configurar contexto de senha
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    # Solicitar nova senha
    print("=== Alterar Senha do Administrador ===\n")
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
    
    print(f"\n✅ Senha do usuário '{username}' alterada com sucesso!")
    print("Você já pode fazer login com a nova senha.")

if __name__ == "__main__":
    alterar_senha()
```

### Passo 2: Executar o script

```bash
python alterar_senha.py
```

### Passo 3: Seguir as instruções

```
=== Alterar Senha do Administrador ===

Nome de usuário (padrão: admin): admin
Digite a nova senha: minha_senha_segura
Confirme a nova senha: minha_senha_segura

✅ Senha do usuário 'admin' alterada com sucesso!
Você já pode fazer login com a nova senha.
```

## Método 2: Via Python Interativo

```bash
python
```

```python
from app.database import get_connection
from passlib.context import CryptContext

# Configurar
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
nova_senha = "sua_senha_super_segura"
username = "admin"

# Gerar hash
hashed = pwd_context.hash(nova_senha)

# Atualizar
conn = get_connection()
cursor = conn.cursor()
cursor.execute('UPDATE user SET password_hash = ? WHERE username = ?', 
               (hashed, username))
conn.commit()
conn.close()

print("Senha alterada com sucesso!")
```

## Método 3: Via SQL Direto (Avançado)

### Passo 1: Gerar o hash da senha

```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
nova_senha = "minha_nova_senha"
hash_gerado = pwd_context.hash(nova_senha)
print(hash_gerado)
```

### Passo 2: Atualizar no banco

```bash
sqlite3 escalas.db
```

```sql
UPDATE user 
SET password_hash = 'COLE_O_HASH_AQUI' 
WHERE username = 'admin';

.quit
```

## Criar Novo Usuário Administrador

```python
from app.database import get_connection
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Dados do novo usuário
novo_username = "gerente"
nova_senha = "senha_do_gerente"

# Gerar hash
hashed = pwd_context.hash(nova_senha)

# Inserir no banco
conn = get_connection()
cursor = conn.cursor()
cursor.execute('INSERT INTO user (username, password_hash) VALUES (?, ?)', 
               (novo_username, hashed))
conn.commit()
conn.close()

print(f"Usuário '{novo_username}' criado com sucesso!")
```

## Listar Todos os Usuários

```python
from app.database import get_connection

conn = get_connection()
cursor = conn.cursor()
cursor.execute('SELECT id, username, created_at FROM user')
users = cursor.fetchall()
conn.close()

print("\n=== Usuários Cadastrados ===")
for user in users:
    print(f"ID: {user[0]} | Usuário: {user[1]} | Criado em: {user[2]}")
```

## Remover Usuário

```python
from app.database import get_connection

username_para_remover = "usuario_antigo"

conn = get_connection()
cursor = conn.cursor()
cursor.execute('DELETE FROM user WHERE username = ?', (username_para_remover,))
conn.commit()
conn.close()

print(f"Usuário '{username_para_remover}' removido com sucesso!")
```

## Dicas de Segurança

### ✅ Boas Práticas

1. **Senha Forte**: Use pelo menos 12 caracteres
2. **Misture**: Letras maiúsculas, minúsculas, números e símbolos
3. **Única**: Não reutilize senhas de outros sistemas
4. **Secreta**: Nunca compartilhe sua senha

### ❌ Evite

- Senhas óbvias: `admin123`, `password`, `123456`
- Informações pessoais: nome, data de nascimento
- Palavras do dicionário
- Sequências: `abcdef`, `qwerty`

### 🔒 Exemplos de Senhas Fortes

- `M3u$ist3m@2024!`
- `Esc@l@sS3gur@#99`
- `@dmin!Str@d0r#2024`

## Recuperação de Senha Perdida

Se você esqueceu a senha do admin, use o Método 2 (Python Interativo) para criar uma nova senha sem precisar da antiga.

## Troubleshooting

### Erro: "module 'bcrypt' has no attribute '__about__'"

Reinstale as dependências:
```bash
pip uninstall bcrypt passlib -y
pip install bcrypt==4.0.1 passlib==1.7.4
```

### Erro: "Database is locked"

Certifique-se de que o servidor não está rodando:
```bash
# Pare o servidor (Ctrl+C)
# Depois execute o script de alteração de senha
```

### Senha não funciona após alteração

1. Verifique se usou o username correto (case-sensitive)
2. Certifique-se de que não há espaços extras
3. Tente fazer logout e login novamente
4. Limpe os cookies do navegador

## Automação com Docker

Se estiver usando Docker, você pode executar o script dentro do container:

```bash
docker exec -it escalas-container python alterar_senha.py
```

Ou criar um novo usuário:

```bash
docker exec -it escalas-container python -c "
from app.database import get_connection
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
hashed = pwd_context.hash('nova_senha_aqui')

conn = get_connection()
cursor = conn.cursor()
cursor.execute('UPDATE user SET password_hash = ? WHERE username = ?', 
               (hashed, 'admin'))
conn.commit()
conn.close()
print('Senha alterada!')
"