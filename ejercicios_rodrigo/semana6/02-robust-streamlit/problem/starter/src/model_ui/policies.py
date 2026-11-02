"""Políticas explícitas que el alumnado puede reutilizar en la UI."""

from dataclasses import dataclass
from typing import get_args

from model_ui.contracts import ConfidenceLevel, LatencyStatus


@dataclass(frozen=True)
class ConfidencePolicy:
    """Umbrales de comunicación, no de aprobación del modelo."""

    low_below: float = 0.60
    high_from: float = 0.85


@dataclass(frozen=True)
class LatencyPolicy:
    """Objetivo técnico de la demo."""

    target_ms: float = 300.0


DEFAULT_CONFIDENCE_POLICY = ConfidencePolicy()
DEFAULT_LATENCY_POLICY = LatencyPolicy()


def classify_confidence(
    confidence: float, policy: ConfidencePolicy = DEFAULT_CONFIDENCE_POLICY
) -> ConfidenceLevel:
    """TODO: valida [0, 1] y devuelve low/medium/high según policy."""
    if confidence < policy.low_below and confidence >= 0:
        return get_args(ConfidenceLevel)[0]
    if confidence >= policy.low_below and confidence < policy.high_from:
        return get_args(ConfidenceLevel)[1]
    if confidence >= policy.high_from and confidence <= 1:
        return get_args(ConfidenceLevel)[2]
    
    raise ValueError(f"La confianza devuelta por el modelo no está en el rango esperado. Rango esperado: entre 0 y 1. Valor recibido: {confidence}")
    

def classify_latency(
    latency_ms: float, policy: LatencyPolicy = DEFAULT_LATENCY_POLICY
) -> LatencyStatus:
    """TODO: devuelve within_target o above_target para una latencia válida."""

    if latency_ms <= policy.target_ms:
        return get_args(LatencyStatus)[0]
    
    return get_args(LatencyStatus)[1]
