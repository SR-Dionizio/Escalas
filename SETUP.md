# SETUP.md - Guia de Configuração do Projeto

## Pré-requisitos

Antes de começar, certifique-se de ter instalado:

- **Python 3.8+** - [Baixar aqui](https://www.python.org/downloads/)
- **pip** - Geralmente vem com Python
- **Git** (opcional) - Para controle de versão

### Windows

1. Baixe Python de https://www.python.org/downloads/
2. **IMPORTANTE**: Marque "Add Python to PATH" durante instalação
3. Abra PowerShell e verifique:
   ```
   python --version
   pip --version
   ```

### Linux/Mac

```bash
# Ubuntu/Debian
sudo apt-get install python3 python3-pip python3-venv

# macOS (com Homebrew)
brew install python3
```

## Instalação do Projeto

### 1. Navegar até o diretório do projeto

```bash
cd d:\Codes\Escalas
```

### 2. Criar ambiente virtual

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar dependências

```bash
pip install -r requirements.txt
```

### 4. Inicializar banco de dados

```bash
python -c "from app.database import init_db; init_db()"
```

Você verá a mensagem: "Database initialized successfully!"

### 5. Iniciar servidor

```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Saída esperada:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

### 6. Acessar aplicação

Abra seu navegador em: **http://localhost:8000**

## Solução de Problemas

### Python não encontrado

**Problema:** Erro "Python não foi encontrado"

**Solução Windows:**
- Abra Painel de Controle > Programas > Desinstalar um programa
- Clique em Python
- Selecione "Repair"
- Marque "Add Python to PATH"

**Solução Linux/Mac:**
```bash
which python3
# Se não encontrar, instale:
sudo apt-get install python3
```

### ModuleNotFoundError: No module named 'fastapi'

**Solução:**
1. Certifique-se que o ambiente virtual está ativado
2. Reinstale as dependências: `pip install -r requirements.txt`

### Porta 8000 em uso

**Solução:**
```bash
# Use outra porta
python -m uvicorn app.main:app --reload --port 8001
```

## Desenvolvimento

### Adicionar novas dependências

```bash
pip install novo-pacote
pip freeze > requirements.txt
```

### Executar em modo debug

Já está habilitado com a flag `--reload`

### Estrutura de pastas

```
app/
├── templates/     # Arquivos HTML (Jinja2)
├── static/        # CSS e JavaScript
├── database.py    # Configuração do banco
├── models.py      # Estruturas de dados
├── services.py    # Lógica de negócio
└── main.py        # Aplicação FastAPI
```

## Produção

### Com Gunicorn

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app.main:app
```

### Com Docker

Veja `Dockerfile` se disponível.

### Em Raspberry Pi

```bash
sudo apt-get install python3-venv python3-pip
# Seguir passos normais de instalação
```

## Documentação

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Bootstrap 5](https://getbootstrap.com/)
- [Jinja2](https://jinja.palletsprojects.com/)

---

Qualquer dúvida? Verifique README.md
