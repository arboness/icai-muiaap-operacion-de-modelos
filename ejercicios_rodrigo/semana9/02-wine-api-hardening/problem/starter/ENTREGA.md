# Entrega — Assignment 9.2 · Wine Quality API 1.1.0

## Evidencias

| Evidencia | Dónde |
| --- | --- |
| API 1.1.0, TODO resueltos | `src/wine_api/` (`grep -rn "TODO S9" src tests` no devuelve nada) |
| Suite completa | `uv run pytest -q` → **38 passed** (27 de aceptación + 11 casos propios parametrizados) |
| Contrato versionado | [`contracts/openapi.json`](contracts/openapi.json), generado con `uv run python -m wine_api.export_openapi` |
| Calidad | `uv run ruff check .` y `uv run ruff format --check .` en verde |
| Captura de `/docs` | [`evidence/docs_s9.png`](evidence/docs_s9.png): `POST /v1/predictions` desplegado con 400, 422 y 503 (`ErrorResponse`) y el selector de ejemplos |

Archivos protegidos (`predictor.py`, `request_id.py`, `dependencies.py` y los
tests de S9.1–S9.3) sin cambios respecto al starter.

## Decisiones

- **S9.1** — `Prediction` declara solo los cuatro campos públicos y usa
  `from_attributes=True` para construirse desde `ModelOutput`; `raw_score` no
  sale ni en la respuesta ni en el contrato. El redondeo de `confidence` (2
  decimales) y el formato de `served_at` (UTC, ISO 8601, milisegundos, sufijo
  `Z`) viven en `field_serializer` del contrato, no en el predictor.
- **S9.2** — Cuatro manejadores registrados en `install_error_handlers`:
  validación (400 `invalid_json` si el cuerpo no es JSON; 422 con `fields` sin
  copiar `input`), `WineApiError` (status/código por atributos de clase),
  `HTTPException` de Starlette (404/405 del enrutado) y `Exception` (500
  genérico; la traza solo va al log con el `request_id`). `/health` lanza
  `ModelUnavailableError`: el dominio no conoce HTTP.
- **S9.3** — `prefix`, `tags` y `responses` 400/422/503 en el `APIRouter`;
  `description` con unidad en los once `Field`; summary, docstring y cuatro
  ejemplos de cuerpo (`valid`, `alcohol_out_of_range`, `wrong_type`,
  `unknown_field`). Metadatos de la app con versión `1.1.0`.
- **S9.4** — 503 con `dependency_overrides` y limpieza en `finally`; nueve
  casos fuera de contrato con `parametrize` (límites, `None`, texto, número en
  string con `strict`, booleano); límites inclusivos de `alcohol` (5 y 20,
  entero y float); snapshot de OpenAPI comparando `render_openapi()` con
  `contracts/openapi.json`, sin red.

## Nota de compatibilidad

La versión pasa de `1.0.0` a `1.1.0` porque todos los cambios son
**compatibles hacia atrás** para los clientes de S7: se **añade** `served_at`
a la respuesta (un cliente que ignora campos desconocidos no se entera), se
dejan de exponer campos internos que nunca formaron parte del contrato
(`raw_score`), `confidence` mantiene tipo y rango y el sobre de error
`{error: {code, message, fields}, request_id}` es el que S7 ya prometía.
Rompería a los clientes, por ejemplo, renombrar `quality_band`, cambiar
`confidence` a porcentaje (0–100), hacer obligatorio un campo nuevo en la
entrada o cambiar los valores de `error.code`. Un cambio así exigiría una
versión mayor (`2.0.0`) publicada en una ruta nueva (`/v2/predictions`),
manteniendo `/v1` un periodo de deprecación anunciado (cabecera `Deprecation`
y nota en `/docs`), y el test de snapshot obliga a que ese cambio sea
deliberado y revisado en el diff de `contracts/openapi.json`.
