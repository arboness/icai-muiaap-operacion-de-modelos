"""Punto de entrada de la API: `fastapi dev` usa `wine_api.main:app`."""

import os
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from wine_api.errors import install_error_handlers
from wine_api.predictor import Predictor, build_predictor
from wine_api.request_id import request_id_middleware
from wine_api.routers import health, predictions

API_VERSION = "1.1.0"  

API_SUMMARY = (
    "Predicción de la calidad de vinos tintos a partir de su análisis fisicoquímico."
)

API_DESCRIPTION = """
Servicio que expone un modelo de ML entrenado sobre el dataset *Wine Quality* (vino tinto).

## `request_id`
Cada petición recibe un identificador único. Si envías la cabecera `X-Request-ID`,
se respeta tu valor; si no, el servidor genera uno. Se devuelve siempre en la
cabecera `X-Request-ID` de la respuesta y dentro del sobre de error.
**Inclúyelo al reportar un problema**: permite localizar la petición en los logs.

## Sobre de error
Todos los errores comparten la misma estructura:

```json
{
  "error": {
    "code": "validation_error",
    "message": "Descripción legible del problema.",
    "request_id": "3f2c9e1a-..."
  }
}
```

- **422**: el cuerpo no cumple el esquema (faltan campos, sobran campos, tipo o rango incorrecto).
- **503**: el modelo aún no está disponible; es temporal, reintenta más tarde.
"""  

OPENAPI_TAGS = [
    {
        "name": "health",
        "description": "Estado del servicio: si está vivo y si está listo para predecir.",
    },
    {
        "name": "predictions",  # ← AJUSTA: el mismo nombre que en tags=[...] del router
        "description": "Predicción de la calidad de un vino a partir de sus once features.",
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