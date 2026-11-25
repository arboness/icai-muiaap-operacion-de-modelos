from dataclasses import asdict
from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Body

from wine_api.dependencies import PredictorDep, RequestIdDep
from wine_api.schemas import VALID_FEATURES_EXAMPLE, ErrorResponse, Prediction, PredictionRequest, PredictionResponse

PREDICTION_EXAMPLES = {
    "valid": {
        "summary": "Válido: vino tinto típico",
        "value": {"features": VALID_FEATURES_EXAMPLE},
    },
    "invalid_out_of_range": {
        "summary": "Inválido: alcohol fuera de rango → 422",
        "description": "`alcohol` debe estar entre 5 y 20 (% vol.).",
        "value": {"features": {**VALID_FEATURES_EXAMPLE, "alcohol": 25.0}},
    },
    "invalid_wrong_type": {
        "summary": "Inválido: número enviado como texto → 422",
        "description": "Las features son estrictas: `\"13.5\"` no se convierte a `13.5`.",
        "value": {"features": {**VALID_FEATURES_EXAMPLE, "alcohol": "13.5"}},
    },
    "invalid_extra_field": {
        "summary": "Inválido: campo no permitido → 422",
        "description": "Dentro de `features` solo se admiten las once variables.",
        "value": {"features": {**VALID_FEATURES_EXAMPLE, "color": "red"}},
    },
}
# TODO S9.3a: mueve aquí `prefix="/v1/predictions"` y `tags=["predictions"]`.

# TODO S9.3c: declara a nivel de router `responses=` para 400, 422 y 503 con
# `{"model": ErrorResponse, "description": ...}`. Así el 422 deja de
# documentarse como `HTTPValidationError`, que ya no es lo que devolvemos.
router = APIRouter(prefix="/v1/predictions", tags=["predictions"],
                   responses={
                       400: {
                           "model": ErrorResponse,
                             "description": "Petición incorrecta."
                             },
                        422: {
                           "model": ErrorResponse,
                             "description": "Error de validación."
                             },
                        503: {
                           "model": ErrorResponse,
                             "description": "Servicio no disponible."
                             }
                   })


@router.post(
    "",
    summary="Predice la calidad de un vino tinto",
    response_description="Calidad predicha y confidence del modelo.",
)
def create_prediction(
    payload: Annotated[PredictionRequest, Body(openapi_examples=PREDICTION_EXAMPLES)],
    predictor: PredictorDep,
    request_id: RequestIdDep,
):
    """
    Recibe las **once variables fisicoquímicas** de un vino tinto y devuelve la
    predicción del modelo. Los rangos y unidades de cada campo están en el esquema
    de `WineFeatures` (todos los rangos son inclusivos).

    **Validación (422)**
    - Faltan campos o se envían campos que no son de las once features.
    - Algún valor está fuera de rango.
    - Algún número se envía como texto (no hay conversión automática de tipos).

    **Respuesta**
    - `prediction`: ...
    - `confidence`: probabilidad entre 0 y 1, redondeada a **N decimales**.
    """
    # TODO S9.3e: añade summary, response_description y un docstring útil para
    # quien consume la API (campos, rangos, decimales de confidence).
    # TODO S9.3f: ofrece en Swagger al menos tres ejemplos de cuerpo (uno válido
    # y dos inválidos). Investiga `Annotated[PredictionRequest, Body(...)]` con
    # `openapi_examples=`; usa VALID_FEATURES_EXAMPLE como base.
    output = predictor.predict(payload.features)
    # TODO S9.1e: este dict expone `raw_score` y la confianza sin redondear.
    # Declara `-> PredictionResponse` y construye el modelo; para pasar de la
    # dataclass ModelOutput a Prediction investiga `from_attributes=True`.
    model_output = Prediction.model_validate(output)
    response = PredictionResponse(
        prediction=model_output, 
        request_id=request_id, 
        served_at=datetime.now(UTC))
    
    return response
