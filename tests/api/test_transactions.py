"""Testes de API do contexto de transações."""

from httpx import AsyncClient


async def test_deposit(client: AsyncClient, auth_headers: dict[str, str], created_account: dict) -> None:
    response = await client.post(
        "/transactions/deposit",
        json={
            "account_id": created_account["id"],
            "amount": "100.00",
            "description": "Depósito inicial",
        },
        headers=auth_headers,
    )

    assert response.status_code == 201
    data = response.json()
    assert data["balance"] == "100.00"
    assert data["transaction"]["type"] == "deposit"


async def test_withdraw_with_sufficient_balance(
    client: AsyncClient,
    auth_headers: dict[str, str],
    created_account: dict,
) -> None:
    await client.post(
        "/transactions/deposit",
        json={"account_id": created_account["id"], "amount": "120.00"},
        headers=auth_headers,
    )

    response = await client.post(
        "/transactions/withdraw",
        json={"account_id": created_account["id"], "amount": "20.00"},
        headers=auth_headers,
    )

    assert response.status_code == 201
    data = response.json()
    assert data["balance"] == "100.00"
    assert data["transaction"]["type"] == "withdrawal"


async def test_withdraw_without_sufficient_balance(
    client: AsyncClient,
    auth_headers: dict[str, str],
    created_account: dict,
) -> None:
    response = await client.post(
        "/transactions/withdraw",
        json={"account_id": created_account["id"], "amount": "10.00"},
        headers=auth_headers,
    )

    assert response.status_code == 400
    assert response.json()["detail"]["message"] == "Saldo insuficiente para realizar o saque."
