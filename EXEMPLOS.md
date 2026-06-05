"""
EXEMPLOS.md - Dados de Exemplo para Testes

Use este arquivo como referência para criar dados de teste na aplicação.
"""

# Exemplo 1: Cadastro de Voluntários

## Voluntário 1
- Nome: João Silva
- Funções: Microfone, Indicador

## Voluntário 2
- Nome: Pedro Oliveira
- Funções: Sistema de Som

## Voluntário 3
- Nome: Carlos Santos
- Funções: Microfone, Sistema de Som, Indicador

## Voluntário 4
- Nome: Marcos Costa
- Funções: Indicador

## Voluntário 5
- Nome: Lucas Ferreira
- Funções: Microfone, Indicador

---

# Exemplo 2: Criação de Escala

## Escala para a semana de 08/06/2026

### Microfone (2 pessoas)
- João Silva
- Carlos Santos

### Sistema de Som (1 pessoa)
- Pedro Oliveira

### Indicadores (2 pessoas)
- Marcos Costa
- Lucas Ferreira

---

# Exemplo 3: Impressão

Quando você clica em "Imprimir Escala", a página mostra:

```
ESCALA DA SEMANA

Data: 08/06/2026

🎤 Microfone:
- João Silva
- Carlos Santos

🔊 Sistema de Som:
- Pedro Oliveira

👁️ Indicadores:
- Marcos Costa
- Lucas Ferreira
```

---

# Como Popular Dados via API

## 1. Criar Voluntários

```bash
curl -X POST http://localhost:8000/api/volunteers \
  -H "Content-Type: application/json" \
  -d '{"nome": "João Silva", "roles": ["MICROFONE", "INDICADOR"]}'
```

## 2. Listar Voluntários

```bash
curl http://localhost:8000/api/volunteers
```

## 3. Criar Escala

```bash
curl -X POST http://localhost:8000/api/schedules \
  -H "Content-Type: application/json" \
  -d '{
    "week_date": "08/06/2026",
    "assignments": {
      "MICROFONE": [1, 3],
      "SOM": [2],
      "INDICADOR": [4, 5]
    }
  }'
```

---

Depois de popular estes dados, você verá tudo funcionando no dashboard!
