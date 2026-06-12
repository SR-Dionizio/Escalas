# Gerenciador de Escalas 📅

Um sistema web para gerenciar escalas semanais de voluntários com funções específicas (Microfone, Som, Indicadores).

## Características

### MVP (Versão 1)
- ✅ **Cadastro de Voluntários**: Registre voluntários com suas funções
- ✅ **Gerenciamento de Escalas**: Crie e visualize escalas semanais
- ✅ **Dashboard**: Veja a escala da semana atual em tempo real
- ✅ **Impressão**: Imprima a escala em formato A4
- ✅ **Indicadores Separados**: Diferencie entre Indicador de Entrada e Indicador do Auditório

### Funcionalidades Futuras (Versão 2)
- 🚀 Geração automática de escalas
- 🚀 Distribuição inteligente de voluntários
- 🚀 Marcação de indisponibilidades
- 🚀 Histórico de escalas

## Tecnologias

- **Backend**: Python + FastAPI
- **Frontend**: HTML5 + Bootstrap 5 + Jinja2
- **Banco de Dados**: SQLite
- **Servidor**: Uvicorn

## Instalação

### Pré-requisitos
- Python 3.8+
- pip

### Passos

1. **Clonar/Baixar o projeto**
```bash
cd Escalas
```

2. **Criar ambiente virtual**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

3. **Instalar dependências**
```bash
pip install -r requirements.txt
```

4. **Inicializar banco de dados**
```bash
python -c "from app.database import init_db; init_db()"
```

5. **Iniciar o servidor**
```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

6. **Acessar a aplicação**
Abra o navegador em: `http://localhost:8000`

## Estrutura do Projeto

```
Escalas/
├── app/
│   ├── templates/
│   │   ├── base.html              # Template base com navbar
│   │   ├── dashboard.html         # Dashboard principal
│   │   ├── voluntarios.html       # Gerenciar voluntários
│   │   ├── escalas.html           # Gerenciar escalas
│   │   └── print.html             # Página de impressão
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css          # Estilos customizados
│   │   └── js/
│   │       └── main.js            # Scripts globais
│   ├── database.py                # Configuração do banco SQLite
│   ├── models.py                  # Modelos de dados
│   ├── services.py                # Lógica de negócio
│   └── main.py                    # Aplicação FastAPI
├── requirements.txt               # Dependências Python
├── escalas.db                     # Banco de dados (criado automaticamente)
└── README.md                      # Este arquivo
```

## Banco de Dados

### Tabelas

| Tabela | Descrição |
|--------|-----------|
| `volunteer` | Registro de voluntários |
| `role` | Tipos de funções (MICROFONE, SOM, INDICADOR_ENTRADA, INDICADOR_AUDITORIO) |
| `volunteer_role` | Relacionamento voluntário-função |
| `schedule` | Escalas semanais |
| `schedule_assignment` | Atribuições de voluntários em escalas |
| `volunteer_unavailable` | Datas em que voluntários estão indisponíveis |

## API Endpoints

### Voluntários
- `GET /api/volunteers` - Listar voluntários
- `POST /api/volunteers` - Criar voluntário
- `GET /api/volunteers/{id}` - Obter voluntário
- `PUT /api/volunteers/{id}` - Atualizar voluntário
- `DELETE /api/volunteers/{id}` - Deletar voluntário

### Escalas
- `GET /api/schedules` - Listar escalas
- `POST /api/schedules` - Criar escala
- `GET /api/schedules/{id}` - Obter escala
- `PUT /api/schedules/{id}` - Atualizar escala
- `DELETE /api/schedules/{id}` - Deletar escala

### Funções
- `GET /api/roles` - Listar funções

### Indisponibilidades
- `POST /api/unavailable` - Marcar voluntário como indisponível

## Páginas Web

### Dashboard (`/`)
Página inicial mostrando a escala da semana atual com:
- Lista de voluntários por função
- Botão para imprimir escala
- Estatísticas gerais

### Voluntários (`/voluntarios`)
Gerenciamento completo de voluntários:
- Listar todos os voluntários
- Cadastrar novo voluntário
- Editar voluntário
- Inativar voluntário

### Escalas (`/escalas`)
Gerenciamento de escalas:
- Visualizar todas as escalas
- Criar nova escala
- Editar escala existente
- Deletar escala
- Histórico de escalas

## Impressão (`/print-week`)

Página formatada para impressão em A4 da escala da semana atual com:
- Data da semana
- Nomes dos voluntários por função
- Formatação otimizada para papel

## Como Usar

### Adicionando um Voluntário

1. Acesse **Voluntários** na navbar
2. Clique em **➕ Novo Voluntário**
3. Preencha o nome
4. Selecione as funções que pode exercer
5. Clique em **Salvar**

### Criando uma Escala

1. Acesse **Escalas** na navbar
2. Clique em **➕ Nova Escala**
3. Selecione a data da semana
4. Escolha 2 voluntários para Microfone
5. Escolha 1 voluntário para Som
6. Escolha 1 voluntário para Indicador de Entrada 🚪
7. Escolha 1 voluntário para Indicador do Auditório 🏛️
8. Clique em **Criar Escala**

### Visualizando a Escala Atual

1. Acesse **Dashboard** (página inicial)
2. Veja a escala da semana atual
3. Use o botão **🖨️ Imprimir Escala** para imprimir

## Configuração de Produção

### Com Gunicorn (recomendado)

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app.main:app
```

### Em Raspberry Pi

```bash
# Instalar dependências do sistema
sudo apt-get update
sudo apt-get install python3-venv python3-pip

# Seguir passos normais de instalação
# Para iniciar automaticamente ao boot, usar systemd service
```

## Migração de Banco de Dados

Se você já tem um banco de dados com a função antiga "INDICADOR", execute o script de migração:

```bash
python migrate_indicadores.py
```

Veja detalhes completos em [MIGRACAO_INDICADORES.md](MIGRACAO_INDICADORES.md)

## Roadmap - Versão 2

- [ ] Geração automática de escalas com IA
- [ ] Distribuição inteligente considerando histórico
- [ ] Sistema de indisponibilidades
- [ ] Exportação em PDF
- [ ] Envio de notificações por email/WhatsApp
- [ ] Histórico de escalas com estatísticas
- [ ] Backup automático
- [ ] Sistema de usuários

## Licença

MIT - Livre para usar e modificar

## Suporte

Para dúvidas ou sugestões, abra uma issue no repositório.

---

Desenvolvido com ❤️ para igrejas e organizações
