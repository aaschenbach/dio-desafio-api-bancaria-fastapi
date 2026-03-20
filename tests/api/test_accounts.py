"""Testes de API do contexto de contas e extratos."""

from httpx import AsyncClient


async def test_create_account(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    response = await client.post(
        "/accounts",
        json={
            "agency": "0001",
            "account_number": "99999-9",
            "owner_name": "Maria de Souza",
            "owner_document": "111.222.333-44",
        },
        headers=auth_headers,
    )

    assert response.status_code == 201
    data = response.json()
    assert data["agency"] == "0001"
    assert data["account_number"] == "99999-9"


async def test_statement(client: AsyncClient, auth_headers: dict[str, str], created_account: dict) -> None:
    await client.post(
        "/transactions/deposit",
        json={"account_id": created_account["id"], "amount": "200.00", "description": "Depósito"},
        headers=auth_headers,
    )
    await client.post(
        "/transactions/withdraw",
        json={"account_id": created_account["id"], "amount": "50.00", "description": "Saque"},
        headers=auth_headers,
    )

    response = await client.get(
        f"/accounts/{created_account['id']}/statement",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["current_balance"] == "150.00"
    assert data["total_deposits"] == "200.00"
    assert data["total_withdrawals"] == "50.00"
    assert data["total_transactions"] == 2
    assert len(data["transactions"]) == 2


async def test_access_without_token(client: AsyncClient) -> None:
    response = await client.get("/accounts")
    assert response.status_code == 401


async def test_access_with_invalid_token(client: AsyncClient) -> None:
    response = await client.get(
        "/accounts",
        headers={"Authorization": "Bearer token-invalido"},
    )
    assert response.status_code == 401
