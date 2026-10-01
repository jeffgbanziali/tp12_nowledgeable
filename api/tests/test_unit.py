import pymysql
import pytest

import app as api_module


class FakeCursor:
    def __init__(self, rows=None):
        self.rows = rows or []
        self.executed = []
        self.lastrowid = 4

    def execute(self, sql, params=None):
        self.executed.append((sql, params))

    def fetchall(self):
        return self.rows

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


class FakeConnection:
    def __init__(self, rows=None):
        self.cur = FakeCursor(rows)
        self.closed = False

    def cursor(self):
        return self.cur

    def close(self):
        self.closed = True


@pytest.fixture
def client():
    api_module.app.config["TESTING"] = True
    return api_module.app.test_client()


@pytest.fixture
def fake_db(monkeypatch):
    conn = FakeConnection(rows=[{"id": 1, "name": "Alice Martin"}, {"id": 2, "name": "Bob Durand"}])
    monkeypatch.setattr(api_module, "get_connection", lambda *a, **k: conn)
    return conn


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def test_list_clients_returns_db_rows(client, fake_db):
    response = client.get("/clients")
    assert response.status_code == 200
    assert response.get_json() == [
        {"id": 1, "name": "Alice Martin"},
        {"id": 2, "name": "Bob Durand"},
    ]
    assert "SELECT" in fake_db.cur.executed[0][0]


def test_list_clients_closes_connection(client, fake_db):
    client.get("/clients")
    assert fake_db.closed is True


def test_add_client_ok(client, fake_db):
    response = client.post("/clients", json={"name": "Jeff"})
    assert response.status_code == 201
    assert response.get_json() == {"id": 4, "name": "Jeff"}
    sql, params = fake_db.cur.executed[0]
    assert "INSERT INTO clients" in sql
    assert params == ("Jeff",)  # requete parametree (pas d'injection SQL)


def test_add_client_missing_name(client, fake_db):
    response = client.post("/clients", json={})
    assert response.status_code == 400
    assert fake_db.cur.executed == []  # la base n'est pas touchee


def test_add_client_invalid_json(client, fake_db):
    response = client.post("/clients", data="pas du json", content_type="application/json")
    assert response.status_code == 400


def test_get_connection_retries_then_fails(monkeypatch):
    calls = []

    def always_fail(**kwargs):
        calls.append(1)
        raise pymysql.MySQLError("db indisponible")

    monkeypatch.setattr(api_module.pymysql, "connect", always_fail)
    monkeypatch.setattr(api_module.time, "sleep", lambda s: None)

    with pytest.raises(pymysql.MySQLError):
        api_module.get_connection(retries=3, delay=0)
    assert len(calls) == 3


def test_get_connection_uses_utf8mb4(monkeypatch):
    captured = {}

    def fake_connect(**kwargs):
        captured.update(kwargs)
        return "connexion"

    monkeypatch.setattr(api_module.pymysql, "connect", fake_connect)
    assert api_module.get_connection() == "connexion"
    assert captured["charset"] == "utf8mb4"