from fastapi import APIRouter

from wine_api.dependencies import PredictorDep, RequestIdDep
from wine_api.errors import ModelUnavailableError
from wine_api.schemas import ErrorResponse, HealthResponse

SERVICE_NAME = "wine-quality-prediction"

router = APIRouter(tags=["health"])


@router.get(
    "/health",
    summary="Comprobar el estado del servicio y del modelo",
    response_description="El servicio está levantado y el modelo cargado.",
    responses={
        503: {
            "model": ErrorResponse,
            "description": "El modelo no está cargado; no se puede predecir.",
        }
    },
)
def read_health(predictor: PredictorDep, request_id: RequestIdDep) -> HealthResponse:
    """Indica si la API puede servir predicciones.

    Úsalo como *readiness probe* antes de enviar tráfico o desde un balanceador.
    Un `200` garantiza que el modelo está cargado e informa de su versión. Un
    `503` con `error.code = "model_unavailable"` significa que el servicio
    responde pero el artefacto de modelo no está listo: reintenta más tarde.
    """

    if not predictor.is_ready():
        raise ModelUnavailableError()
    return HealthResponse(
        status="ok",
        service=SERVICE_NAME,
        model_status="ready",
        model_version=predictor.model_version,
        request_id=request_id,
    )
