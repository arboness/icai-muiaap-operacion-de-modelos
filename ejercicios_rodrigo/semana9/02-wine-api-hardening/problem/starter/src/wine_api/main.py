"""Punto de entrada de la API: `fastapi dev` usa `wine_api.main:app`."""

import os
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from wine_api.errors import install_error_handlers
from wine_api.predictor import Predictor, build_predictor
from wine_api.request_id import request_id_middleware
from wine_api.routers import health, predictions

# 1.1.0: cambio menor y compatible (se añade `served_at`, se filtran campos
# internos y se documenta el contrato existente sin romper a los clientes de S7).
API_VERSION = "1.1.0"
API_SUMMARY = "Predicción de la calidad de vinos tintos a partir de su analítica."
API_DESCRIPTION = """
Servicio de inferencia de la asignatura Operación de Modelos.

## Trazabilidad

Cada respuesta incluye la cabecera `X-Request-Id` y el mismo valor en el campo
`request_id` del cuerpo, también en los errores. Cítalo al reportar una
incidencia: es la clave para encontrar la petición en los logs.

## Errores

Todos los errores comparten un único sobre `ErrorResponse`:

```json
{"error": {"code": "validation_error", "message": "...",
  "fields": [{"field": "features.alcohol", "message": "..."}]},
 "request_id": "req_..."}
```

Programa contra `error.code` (estable), no contra `error.message`. `fields`
solo aparece en errores de validación (`422`). Ningún error devuelve trazas ni
los datos enviados.
"""
OPENAPI_TAGS = [
    {
        "name": "health",
        "description": "Estado del servicio y del modelo (readiness).",
    },
    {
        "name": "predictions",
        "description": "Inferencia de la banda de calidad de un vino tinto.",
    },
]


def create_app(predictor: Predictor | None = None) -> FastAPI:
    """Crea la aplicación; los tests inyectan su propio predictor."""

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
        app.state.predictor = predictor or build_predictor(
            os.environ.get("WINE_API_MODE", "ready")
        )
        yield

    app = FastAPI(
        title="Wine Quality API",
        version=API_VERSION,
        summary=API_SUMMARY,
        description=API_DESCRIPTION,
        openapi_tags=OPENAPI_TAGS,
        lifespan=lifespan,
    )
    app.middleware("http")(request_id_middleware)
    install_error_handlers(app)
    app.include_router(health.router)
    app.include_router(predictions.router)
    return app


app = create_app()
