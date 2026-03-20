# API Bancária FastAPI

API RESTful assíncrona para contas correntes, depósitos, saques e extrato, construída com FastAPI seguindo a arquitetura em camadas definida em `FASTAPI.md`.

## Visão geral do projeto

O projeto implementa:

- registro e autenticação de usuários com JWT;
- criação de contas correntes vinculadas ao usuário autenticado;
- depósitos e saques com validação de saldo;
- extrato completo com totais e saldo atual;
- documentação automática via Swagger/OpenAPI;
- testes de API, integração e unidade.

## Stack utilizada

- Python 3.13
- FastAPI
- SQLAlchemy 2.x com `AsyncSession`
- SQLite com `aiosqlite`
- Pydantic v2
- JWT com `python-jose`
- Hash de senha com `pwdlib`
- Pytest

## Estrutura de pastas

```text
app/
├── core/
├── models/
├── repositories/
├── routers/
├── schemas/
├── services/
├── database.py
└── main.py

tests/
├── api/
├── integration/
├── unit/
└── conftest.py
```

## Como instalar dependências

```powershell
uv sync
```

## Como configurar variáveis de ambiente

1. Copie `.env.example` para `.env`.
2. Ajuste as variáveis conforme necessário.

Variáveis principais:

- `DATABASE_URL`
- `JWT_SECRET_KEY`
- `JWT_ALGORITHM`
- `ACCESS_TOKEN_EXPIRE_MINUTES`

## Como executar localmente

```powershell
uv run uvicorn app.main:app --reload
```

## Como rodar testes

```powershell
uv run pytest --cov=app --cov-report=term-missing -q
```

## Como acessar Swagger

Com a aplicação em execução:

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

## Fluxo de uso

### Registrar usuário

```http
POST /auth/register
Content-Type: application/json

{
  "username": "joaosilva",
  "email": "joao@example.com",
  "password": "Senha123"
}
```

### Autenticar

```http
POST /auth/login
Content-Type: application/json

{
  "username_or_email": "joaosilva",
  "password": "Senha123"
}
```

### Criar conta

```http
POST /accounts
Authorization: Bearer <token>
Content-Type: application/json

{
  "agency": "0001",
  "account_number": "12345-6",
  "owner_name": "João da Silva",
  "owner_document": "123.456.789-00"
}
```

### Depositar

```http
POST /transactions/deposit
Authorization: Bearer <token>
Content-Type: application/json

{
  "account_id": 1,
  "amount": 200.00,
  "description": "Depósito inicial"
}
```

### Sacar

```http
POST /transactions/withdraw
Authorization: Bearer <token>
Content-Type: application/json

{
  "account_id": 1,
  "amount": 50.00,
  "description": "Saque"
}
```

### Consultar extrato

```http
GET /accounts/1/statement
Authorization: Bearer <token>
```

## Decisões de desenho

- `GET /accounts` retorna apenas as contas do usuário autenticado.
- O saldo é calculado a partir das transações, sem persistência física adicional.
- A autenticação foi centralizada em `core/security.py` e `core/dependencies.py`.
