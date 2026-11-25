from fastapi import APIRouter, HTTPException

from wine_api.dependencies import PredictorDep, RequestIdDep
from wine_api.schemas import ErrorResponse, HealthResponse  # noqa: F401 - pista para S9.1d

SERVICE_NAME = "wine-quality-prediction"

# TODO S9.3a: declara `tags=["health"]` en el router, no en include_router().
router = APIRouter(tags=['health'], prefix="/health")



# TODO S9.3b: añade `summary=`, `response_description=` y un docstring que diga
# cuándo usar el endpoint y qué significa un 503. Documenta el 503 con
# `responses={503: {"model": ErrorResponse, "description": ...}}`.
@router.get("",
    summary="Comprueba si el servicio está listo para recibir peticiones",
    response_description="El servicio está listo: modelo cargado y dependencias disponibles.",
    responses={
        503: {
            "model": ErrorResponse,
            "description": "El servicio está levantado pero todavía no puede atender peticiones.",
        }
    },
)
def read_health(predictor: PredictorDep, request_id: RequestIdDep):
    # TODO S9.2f: sustituye el HTTPException por `ModelUnavailableError`: el
    # dominio no debería saber de HTTP y el manejador produce el sobre común.
    """
    Comprueba que el servicio está vivo **y** listo para predecir.

    Úsalo antes de enviar predicciones, o como readiness probe (Docker,
    Kubernetes, balanceador) para decidir si se le puede mandar tráfico.

    - **200**: el modelo está cargado; se pueden hacer predicciones.
    - **503**: el proceso está levantado pero el modelo no está disponible
      (todavía cargando o fallo al cargar). Es temporal: espera y reintenta.
    """
    if not predictor.is_ready():
        raise HTTPException(status_code=503, detail="Model not ready")
    # TODO S9.1d: declara `-> HealthResponse` y devuelve una instancia.
    return {
        "status": "ok",
        "service": SERVICE_NAME,
        "model_status": "ready",
        "model_version": predictor.model_version,
        "request_id": request_id,
    }
