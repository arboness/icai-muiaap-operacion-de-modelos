"""S9.4 — Tests que escribe el alumnado.

Cada test empieza en rojo con `pytest.fail`. Sustituye esa línea por el test
real; la entrega se considera completa cuando toda la suite está en verde.
"""

import pytest
from fastapi.testclient import TestClient

from wine_api.dependencies import get_predictor  # noqa: F401 - pista S9.4a
from wine_api.predictor import UnavailablePredictor  # noqa: F401 - pista S9.4a


def test_prediction_returns_503_when_model_is_unavailable(
    client: TestClient, valid_payload: dict
) -> None:
    client.app.dependency_overrides[get_predictor] = lambda: UnavailablePredictor()
    try:
        response = client.post("/v1/predictions", json=valid_payload)

        assert response.status_code == 503
        assert response.json()["error"]["code"] == "model_unavailable"  # ← el code real
    finally:
        client.app.dependency_overrides.pop(get_predictor, None)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        pytest.param("alcohol", 4.99, id="alcohol-justo-por-debajo"),
        pytest.param("alcohol", 20.01, id="alcohol-justo-por-encima"),
        pytest.param("ph", 2.49, id="ph-justo-por-debajo"),
        pytest.param("density", 1.011, id="density-justo-por-encima"),
        pytest.param("fixed_acidity", -0.01, id="fixed_acidity-negativa"),
        pytest.param("ph", None, id="ph-none"),
        pytest.param("alcohol", "13.5", id="alcohol-texto"),
    ],
)
def test_out_of_contract_values_are_rejected(
    client: TestClient, valid_payload: dict, field: str, value: object
) -> None:
    payload = {**valid_payload, "features": {**valid_payload["features"], field: value}}

    response = client.post("/v1/predictions", json=payload)

    assert response.status_code == 422
    assert [f["field"] for f in response.json()["error"]["fields"]] == [f"features.{field}"]

@pytest.mark.parametrize("alcohol", [5.0, 20.0], ids=["minimo", "maximo"])
def test_range_limits_are_inclusive(
    client: TestClient, valid_payload: dict, alcohol: float
) -> None:
    payload = {**valid_payload, "features": {**valid_payload["features"], "alcohol": alcohol}}

    response = client.post("/v1/predictions", json=payload)

    assert response.status_code == 200, response.json()