# Sistema de Autenticação

## Visão Geral

O sistema agora possui autenticação para proteger as páginas de gerenciamento. O dashboard continua público para visualização.

## Páginas Públicas (Sem Login)

- **Dashboard** (`/`) - Visualização das escalas do mês
- **Impressão** (`/print-month`) - Impressão das escalas
- **Login** (`/login`) - Página de login

## Páginas Protegidas (Requer Login)

- **Voluntários** (`/voluntarios`) - Gerenciamento de voluntários
- **Escalas** (`/escalas`) - Criação e edição de escalas

## APIs Protegidas

Todas as operações de criação, edição e exclusão requerem autenticação:

- `POST /api/volunteers` - Criar voluntário
- `PUT /api/volunteers/{id}` - Editar voluntário
- `DELETE /api/volunteers/{id}` - Deletar voluntário
- `POST /api/schedules` - Criar escala
- `PUT /api/schedules/{id}` - Editar escala
- `DELETE /api/schedules/{id}` - Deletar escala

## APIs Públicas

- `GET /api/volunteers` - Listar voluntários
- `GET /api/volunteers/{id}` - Ver voluntário
- `GET /api/roles` - Listar funções
- `GET /api/schedules` - Listar escalas
- `GET /api/schedules/{id}` - Ver escala

## Credenciais Padrão

**Usuário:** `admin`  
**Senha:** `admin123`

⚠️ **IMPORTANTE:** Altere a senha padrão em produção!

## Como Funciona

### 1. Login
- Usuário acessa `/login`
- Insere credenciais
- Sistema valida no banco de dados
- Se válido, cria um token JWT
- Token é armazenado em cookie HTTP-only

### 2. Autenticação
- Cada requisição protegida verifica o cookie
- Token é validado
- Se válido, permite acesso
- Se inválido ou ausente, retorna erro 401

### 3. Logout
- Usuário clica em "Sair"
- Cookie é removido
- Redirecionado para dashboard

## Segurança

### Senhas
- Armazenadas com hash bcrypt
- Nunca armazenadas em texto plano

### Tokens
- JWT com expiração de 24 horas
- Assinados com chave secreta
- Armazenados em cookies HTTP-only (protege contra XSS)

### Cookies
- `httponly=True` - Não acessível via JavaScript
- `samesite=lax` - Proteção contra CSRF
- `max_age=86400` - Expira em 24 horas

## Alterando a Senha do Admin

### Via Python:

```python
from app.database import get_connection
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
new_password = "sua_nova_senha_segura"
hashed = pwd_context.hash(new_password)

conn = get_connection()
cursor = conn.cursor()
cursor.execute('UPDATE user SET password_hash = ? WHERE username = ?', 
               (hashed, 'admin'))
conn.commit()
conn.close()

print("Senha alterada com sucesso!")
```

### Via SQL:

```sql
-- Primeiro, gere o hash da senha em Python:
-- from passlib.context import CryptContext
-- pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
-- print(pwd_context.hash("nova_senha"))

-- Depois execute:
UPDATE user SET password_hash = 'HASH_GERADO_AQUI' WHERE username = 'admin';
```

## Criando Novos Usuários

```python
from app.database import get_connection
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

username = "novo_usuario"
password = "senha_segura"
hashed = pwd_context.hash(password)

conn = get_connection()
cursor = conn.cursor()
cursor.execute('INSERT INTO user (username, password_hash) VALUES (?, ?)', 
               (username, hashed))
conn.commit()
conn.close()

print(f"Usuário {username} criado com sucesso!")
```

## Comportamento da Interface

### Quando NÃO está logado:
- Navbar mostra apenas "Dashboard" e botão "🔐 Login"
- Dashboard é acessível (somente leitura)
- Tentar acessar `/voluntarios` ou `/escalas` redireciona para erro 401

### Quando está logado:
- Navbar mostra "Dashboard", "Voluntários", "Escalas"
- Mostra nome do usuário (👤 admin)
- Botão "Sair" disponível
- Todas as páginas de gerenciamento acessíveis

## Troubleshooting

### "Não autenticado" ao tentar acessar páginas protegidas
- Verifique se está logado
- Verifique se o cookie não expirou (24h)
- Tente fazer logout e login novamente

### Senha não funciona
- Verifique se está usando as credenciais corretas
- Usuário: `admin` (minúsculo)
- Senha: `admin123`

### Cookie não persiste
- Verifique se o navegador aceita cookies
- Verifique se não está em modo anônimo/privado

## Melhorias Futuras

- [ ] Sistema de recuperação de senha
- [ ] Múltiplos níveis de permissão
- [ ] Registro de auditoria (quem fez o quê)
- [ ] Autenticação de dois fatores (2FA)
- [ ] Integração com OAuth (Google, Microsoft)