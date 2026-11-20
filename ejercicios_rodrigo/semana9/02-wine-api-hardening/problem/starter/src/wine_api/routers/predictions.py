import copy
from datetime import UTC, datetime
from typing import Annotated, Any

from fastapi import APIRouter, Body

from wine_api.dependencies import PredictorDep, RequestIdDep
from wine_api.schemas import (
    VALID_FEATURES_EXAMPLE,
    ErrorResponse,
    Prediction,
    PredictionRequest,
    PredictionResponse,
)


def _features_with(**changes: Any) -> dict[str, Any]:
    features = copy.deepcopy(VALID_FEATURES_EXAMPLE)
    features.update(changes)
    return {"features": features}


PREDICTION_EXAMPLES = {
    "valid": {
        "summary": "Vino tinto válido",
        "description": "Once variables dentro de rango: devuelve 200.",
        "value": {"features": copy.deepcopy(VALID_FEATURES_EXAMPLE)},
    },
    "alcohol_out_of_range": {
        "summary": "Alcohol fuera de rango: 422",
        "description": "`alcohol` debe estar entre 5 y 20 (% vol.).",
        "value": _features_with(alcohol=25.0),
    },
    "wrong_type": {
        "summary": "Tipo incorrecto: 422",
        "description": "`density` es un texto en lugar de un número.",
        "value": _features_with(density="alta"),
    },
    "unknown_field": {
        "summary": "Campo no declarado: 422",
        "description": "El contrato rechaza campos extra como `color`.",
        "value": _features_with(color="red"),
    },
}

router = APIRouter(
    prefix="/v1/predictions",
    tags=["predictions"],
    responses={
        400: {"model": ErrorResponse, "description": "El cuerpo no es JSON válido."},
        422: {
            "model": ErrorResponse,
            "description": "El cuerpo no cumple el contrato; `error.fields` "
            "indica qué campos fallan.",
        },
        503: {
            "model": ErrorResponse,
            "description": "El modelo no está cargado; reintenta más tarde.",
        },
    },
)


@router.post(
    "",
    summary="Predecir la banda de calidad de un vino tinto",
    response_description="Banda de calidad, confianza y versiones del modelo.",
)
def create_prediction(
    payload: Annotated[PredictionRequest, Body(openapi_examples=PREDICTION_EXAMPLES)],
    predictor: PredictorDep,
    request_id: RequestIdDep,
) -> PredictionResponse:
    """Estima la banda de calidad a partir de once variables fisicoquímicas.

    - `features`: once campos numéricos obligatorios con rangos **inclusivos**
      (ver el esquema `WineFeatures`); no se admiten campos extra, booleanos ni
      textos.
    - `prediction.quality_band`: `needs_review`, `acceptable` o `excellent`.
    - `prediction.confidence`: entre 0 y 1, redondeada a **dos decimales**.
    - `served_at`: instante de la inferencia en UTC (ISO 8601 con sufijo `Z`).
    - `request_id`: coincide con la cabecera `X-Request-Id`; cítalo al reportar
      una incidencia.

    La predicción es docente: no sustituye la cata ni una certificación.
    """

    output = predictor.predict(payload.features)
    return PredictionResponse(
        prediction=Prediction.model_validate(output),
        request_id=request_id,
        served_at=datetime.now(UTC),
    )
