# Assignment 9.1 — Microejercicios M1–M4

Copia de las demos de `semana9/modules/09-api-professional` (`examples/`,
`tests/`, `pyproject.toml`, `uv.lock`) sobre la que se han hecho los
microejercicios. El enunciado está en [ENUNCIADO.md](ENUNCIADO.md).

```bash
uv sync --locked
uv run pytest -q        # 10 passed (9 originales + test de M4)
uv run ruff check .     # All checks passed
```

Cambios que se conservan: el ejemplo `no_income` de M3 (con el test que cuenta
ejemplos adaptado) y el test nuevo de M4. Los cambios temporales de M2 (comentar
`handle_validation`) y M4 (quitar `raise_server_exceptions=False`) se hicieron
y se deshicieron.

## M1 — Serialización

`/v1/scores/leaky`:

```json
{"band": "acceptable", "confidence": 0.8312377, "raw_score": 6.137,
 "threshold_config": "/srv/models/thresholds.yaml"}
```

`/v1/scores/public`:

```json
{"band": "acceptable", "confidence": 0.83, "served_at": "2026-11-20T11:02:38.917831Z",
 "note": null, "is_reliable": true}
```

1. Campos que solo aparecen en `leaky`: **`raw_score`** y **`threshold_config`**
   (además `confidence` sale sin redondear, 0.8312377). Son internos del
   modelo; `threshold_config` además filtra una ruta del servidor.
2. `/v1/scores/filtered` devuelve un `dict` con todo, pero declara
   **`response_model=PublicScore`**: FastAPI valida el valor de retorno contra
   ese modelo y **descarta todos los campos que el modelo no declara** antes de
   serializar, aplicando además sus `field_serializer` (redondeo, `Z`).
3. Sí: en `/docs` el esquema `PublicScore` incluye `is_reliable` (boolean,
   solo lectura), porque es un `@computed_field` y forma parte del esquema de
   serialización.

## M2 — Errores

| Petición | Status | `error.code` | `error.fields` |
| --- | ---: | --- | --- |
| `POST /v1/scores` `{"age": 30, "income": 1000}` | 200 | — (respuesta `{"score": 0.01}`) | — |
| `POST /v1/scores` `{"age": "treinta", "income": 1000}` | 422 | `validation_error` | `[{"field": "age", "message": "Input should be a valid integer, unable to parse string as an integer"}]` |
| `POST /v1/scores` `{"age": 30}` | 422 | `validation_error` | `[{"field": "income", "message": "Field required"}]` |
| `GET /v1/nada` | 404 | `not_found` | — |
| `GET /v1/boom` | 500 | `internal_error` | — |

Todas las respuestas de error tienen `error` en la raíz y ninguna contiene
`TU_SECRETO`: el manejador genérico solo escribe la traza en el log del
servidor (`logger.exception`).

Con el decorador de `handle_validation` comentado, el segundo caso devuelve el
formato por defecto de FastAPI:

```json
{"detail": [{"type": "int_parsing", "loc": ["body", "age"],
  "msg": "Input should be a valid integer, unable to parse string as an integer",
  "input": "treinta"}]}
```

Rompe el sobre común (`detail` en vez de `error`) y además **devuelve el input
del cliente**. El decorador quedó restaurado.

## M3 — OpenAPI

En `/openapi.json`, todo cae en `paths["/v1/scores"]["post"]`:

- `summary=` del decorador → `"summary"`.
- Docstring de `create_score` → `"description"` (Markdown).
- `response_description=` → `responses["200"].description`.
- `responses=` del `APIRouter` → `responses["422"]` y `responses["503"]`, con
  `$ref: #/components/schemas/ErrorResponse`.
- `openapi_examples` → `requestBody.content["application/json"].examples`.

El ejemplo `minor` con *Try it out* devuelve 422 (`age` debe ser ≥ 18; esta demo
no tiene manejador propio, así que sale el `{"detail": ...}` por defecto).

Se ha añadido un tercer ejemplo `no_income` (`{"age": 42}`); el desplegable de
Swagger muestra `valid`, `minor` y `no_income`, y
`test_openapi_documents_errors_and_examples` se ha adaptado a los tres.

## M4 — Tests

- El test con `dependency_overrides` es
  `test_dependency_override_simulates_unavailable_model`: sustituye `get_model`
  por un modelo con `ready = False` para provocar el 503 sin tocar el código, y
  el fixture `errors_client` limpia los overrides al terminar.
- Sin `raise_server_exceptions=False`, `TestClient` **re-lanza en el test la
  excepción no controlada** (`RuntimeError: password=TU_SECRETO ...`) en vez de
  devolver la respuesta 500 que generaría el servidor, así que
  `test_unexpected_error_hides_secrets` falla con la excepción. Con el flag se
  prueba lo que vería el cliente real. Cambio restaurado.
- Test nuevo `test_zero_income_is_rejected`: `income: 0` → 422 con
  `fields[0].field == "income"`.

```text
$ uv run pytest -q
..........                                                               [100%]
10 passed
```
