# Migração: Separação de Indicadores

## O que mudou?

O sistema foi atualizado para separar a função "INDICADOR" em duas funções distintas:
- **INDICADOR_ENTRADA** 🚪 - Indicador de Entrada
- **INDICADOR_AUDITORIO** 🏛️ - Indicador do Auditório

## Como migrar o banco de dados existente

### Passo 1: Backup (IMPORTANTE!)

Antes de fazer qualquer alteração, faça backup do banco de dados:

```bash
# Windows
copy escalas.db escalas_backup.db

# Linux/Mac
cp escalas.db escalas_backup.db
```

### Passo 2: Executar o script de migração

Execute o script de migração que irá:
1. Criar as novas funções INDICADOR_ENTRADA e INDICADOR_AUDITORIO
2. Migrar todos os voluntários que tinham INDICADOR para terem ambas as novas funções
3. Migrar as escalas existentes (primeiro indicador vira ENTRADA, segundo vira AUDITORIO)
4. Remover a função antiga INDICADOR

```bash
python migrate_indicadores.py
```

**Saída esperada:**
```
Iniciando migração...
Adicionando novas funções...
Migrando voluntários...
✓ X voluntários migrados
Migrando escalas...
✓ Y escalas migradas
Removendo função antiga...

✅ Migração concluída com sucesso!
As funções agora são:
  - MICROFONE
  - SOM
  - INDICADOR_ENTRADA
  - INDICADOR_AUDITORIO
```

### Passo 3: Reiniciar o servidor

Após a migração, reinicie o servidor:

```bash
# Parar o servidor (Ctrl+C)
# Iniciar novamente
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## O que acontece com os dados existentes?

### Voluntários
- Todos os voluntários que tinham a função "INDICADOR" agora terão **ambas** as funções:
  - INDICADOR_ENTRADA
  - INDICADOR_AUDITORIO
- Você pode editar cada voluntário depois para remover uma das funções se necessário

### Escalas
- Para cada escala existente com indicadores:
  - O **primeiro** indicador será convertido para **INDICADOR_ENTRADA**
  - O **segundo** indicador será convertido para **INDICADOR_AUDITORIO**
- Se uma escala tinha apenas 1 indicador, ele será convertido para ENTRADA

## Novas funcionalidades

### Dashboard
Agora mostra os dois tipos de indicadores separadamente:
- 🚪 **Indicador de Entrada** (card amarelo)
- 🏛️ **Indicador do Auditório** (card azul)

### Página de Escalas
- Ao criar/editar uma escala, você escolhe:
  - 2 Microfones
  - 1 Som
  - 1 Indicador de Entrada (radio button)
  - 1 Indicador do Auditório (radio button)

### Página de Voluntários
- Ao cadastrar/editar voluntários, você pode selecionar:
  - ☑️ Microfone
  - ☑️ Som
  - ☑️ 🚪 Indicador de Entrada
  - ☑️ 🏛️ Indicador do Auditório

### Impressão
A página de impressão também mostra os dois tipos separadamente.

## Rollback (em caso de problemas)

Se algo der errado, você pode restaurar o backup:

```bash
# Windows
copy escalas_backup.db escalas.db

# Linux/Mac
cp escalas_backup.db escalas.db
```

## Banco de dados novo (sem migração)

Se você está iniciando um banco de dados do zero, não precisa executar a migração.
O sistema já criará as funções corretas automaticamente:

```bash
python -c "from app.database import init_db; init_db()"
```

## Verificação

Após a migração, você pode verificar se tudo está correto:

1. Acesse http://localhost:8000/voluntarios
   - Verifique se os voluntários têm as novas funções

2. Acesse http://localhost:8000/escalas
   - Verifique se as escalas existentes mostram os indicadores corretamente

3. Acesse http://localhost:8000/
   - Verifique se o dashboard mostra os dois tipos de indicadores separadamente

## Suporte

Se encontrar problemas durante a migração:
1. Restaure o backup
2. Verifique os logs de erro
3. Abra uma issue no repositório com detalhes do erro