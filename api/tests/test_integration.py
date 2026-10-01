python
import os
import uuid

import pytest
import requests


BASE_URL = os.getenv("API_URL", "http://localhost:5000")

pytestmark = pytest.mark.integration


@pytest.fixture(scope="module", autouse=True)
def stack_disponible():
    """
    Vérifie que l'API est disponible avant de lancer les tests E2E.

    En CI, API_URL est défini explicitement.
    Si l'API est inaccessible, les tests doivent échouer
    plutôt que d'être ignorés.
    """
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        response.raise_for_status()
    except requests.exceptions.RequestException as exc:
        pytest.fail(
            f"API injoignable sur {BASE_URL}. "
            f"Vérifie que la stack Docker est démarrée. "
            f"Erreur : {exc}"
        )


def test_who():
    response = requests.get(f"{BASE_URL}/who", timeout=5)

    assert response.status_code == 200
    assert response.text.strip() != ""


def test_health():
    response = requests.get(f"{BASE_URL}/health", timeout=5)

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_clients_initialises_par_init_sql():
    response = requests.get(f"{BASE_URL}/clients", timeout=5)

    assert response.status_code == 200

    names = [client["name"] for client in response.json()]

    assert "Alice Martin" in names
    assert "Bob Durand" in names
    assert "Chloé Bernard" in names


def test_ajout_puis_lecture_depuis_mysql():
    name = f"Test-{uuid.uuid4().hex[:8]}"

    response = requests.post(
        f"{BASE_URL}/clients",
        json={"name": name},
        timeout=5,
    )

    assert response.status_code == 201

    response = requests.get(
        f"{BASE_URL}/clients",
        timeout=5,
    )

    assert response.status_code == 200

    names = [client["name"] for client in response.json()]

    assert name in names


def test_ajout_sans_nom_refuse():
    response = requests.post(
        f"{BASE_URL}/clients",
        json={},
        timeout=5,
    )

    assert response.status_code == 400

