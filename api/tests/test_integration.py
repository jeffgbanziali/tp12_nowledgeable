import uuid

import pytest
import requests

BASE_URL = "http://localhost:5000"

pytestmark = pytest.mark.integration


@pytest.fixture(scope="module", autouse=True)
def stack_disponible():
    try:
        requests.get(f"{BASE_URL}/health", timeout=3)
    except requests.exceptions.RequestException:
        pytest.skip("Stack Docker non demarree (lancer: docker compose up -d)")


def test_health():
    r = requests.get(f"{BASE_URL}/health", timeout=5)
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_clients_initialises_par_init_sql():
    r = requests.get(f"{BASE_URL}/clients", timeout=5)
    assert r.status_code == 200
    names = [c["name"] for c in r.json()]
    assert "Alice Martin" in names
    assert "Bob Durand" in names
    assert "Chloé Bernard" in names  # verifie aussi l'encodage utf8mb4


def test_ajout_puis_lecture_depuis_mysql():
    name = f"Test-{uuid.uuid4().hex[:8]}"
    r = requests.post(f"{BASE_URL}/clients", json={"name": name}, timeout=5)
    assert r.status_code == 201

    names = [c["name"] for c in requests.get(f"{BASE_URL}/clients", timeout=5).json()]
    assert name in names


def test_ajout_sans_nom_refuse():
    r = requests.post(f"{BASE_URL}/clients", json={}, timeout=5)
    assert r.status_code == 400