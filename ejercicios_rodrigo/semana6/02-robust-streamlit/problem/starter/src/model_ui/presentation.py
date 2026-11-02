"""TODOs de la vista UX: copy de salida y traducción de errores."""

from __future__ import annotations

from model_ui.contracts import ConfidenceLevel, PredictionPayload, PredictionView, UserFacingError
from model_ui.errors import ArtifactUnavailableError, InferenceTimeoutError, InputContractError
from model_ui.policies import (
    DEFAULT_CONFIDENCE_POLICY,
    DEFAULT_LATENCY_POLICY,
    ConfidencePolicy,
    LatencyPolicy,
    classify_confidence,
    classify_latency,
)
from pydantic import ValidationError

QUALITY_LABELS = {
    "needs_review": "Requiere revisión",
    "acceptable": "Resultado aceptable",
    "excellent": "Resultado excelente",
}

CONFIDENCE_COPY = {
    "low": (
        "Confianza baja",
        "El resultado es orientativo y requiere revisión; "
        "la confianza no es una garantía.",
    ),
    "medium": (
        "Confianza intermedia",
        "Usa el resultado como señal orientativa y revisa su contexto antes de actuar.",
    ),
    "high": (
        "Confianza alta",
        "La confianza es alta para este modelo, pero no garantiza "
        "que la decisión sea correcta.",
    ),
}

LATENCY_COPY = {
    "within_target": (
        "Dentro del objetivo",
        "La respuesta quedó dentro del objetivo de la demo.",
    ),
    "above_target": (
        "Por encima del objetivo",
        "La respuesta llegó, pero la latencia supera el objetivo técnico de la demo.",
    ),
}


def build_prediction_view(
    prediction: PredictionPayload,
    latency_ms: float,
    *,
    confidence_policy: ConfidencePolicy = DEFAULT_CONFIDENCE_POLICY,
    latency_policy: LatencyPolicy = DEFAULT_LATENCY_POLICY,
) -> PredictionView:
    """TODO: construye la vista con etiquetas, confianza, latencia y versiones."""
    
    confidence_level= classify_confidence(prediction.confidence, confidence_policy)
    confidence_label = str(classify_confidence(prediction.confidence, confidence_policy))
    latency_status = classify_latency(latency_ms, latency_policy)
    latency_label = str(classify_latency(latency_ms, latency_policy))


    if confidence_label == "low":
        confidence_message = f"Confianza baja: requiere revisión. La confianza no es una garantía."
    elif confidence_label == "medium":
        confidence_message = f"Confianza media. La confianza no es una garantía."
    else:
        confidence_message = f"Confianza alta. La confianza no es una garantía."
        
    return PredictionView(
        quality_band = prediction.quality_band,
        quality_label = str(prediction.quality_band),
        confidence = prediction.confidence,
        confidence_level= confidence_level,
        confidence_label = confidence_label,
        confidence_message = confidence_message,
        latency_ms = latency_ms,
        latency_status = latency_status,
        latency_label = latency_label,
        latency_message ="la latencia es ",
        model_version = prediction.model_version,
        preprocessing_version = prediction.preprocessing_version
    )


def to_user_facing_error(error: Exception, request_id: str) -> UserFacingError:
    """Asigna código estable, mensaje accionable y recuperación."""
    if isinstance(error, InputContractError):
        return UserFacingError(
            code="invalid_input",
            title="Datos de entrada no válidos",
            message="Algún valor está fuera de rango o tiene un formato incorrecto.",
            recovery="Revisa los valores introducidos y vuelve a intentarlo.",
            request_id=request_id,
        )

    if isinstance(error, InferenceTimeoutError):
        return UserFacingError(
            code="timeout",
            title="El modelo ha tardado demasiado",
            message="La predicción no se completó a tiempo.",
            recovery="Espera unos segundos y vuelve a intentarlo.",
            request_id=request_id,
        )
    if isinstance(error, ArtifactUnavailableError):
        return UserFacingError(
            code="artifact_unavailable",
            title="Modelo no disponible",
            message="No se ha podido cargar el modelo o sus artefactos.",
            recovery="Inténtalo de nuevo más tarde. Si persiste, avisa al equipo técnico.",
            request_id=request_id,
        )

    return UserFacingError(
        code="prediction_error",
        title="No se pudo completar la predicción",
        message="Ha ocurrido un problema al procesar la predicción.",
        recovery=f"Vuelve a intentarlo. Si persiste, indica el código {request_id}.",
        request_id=request_id,
    )