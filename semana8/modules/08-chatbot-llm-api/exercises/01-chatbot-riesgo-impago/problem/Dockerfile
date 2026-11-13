# Imagen unica para la API y el frontend (docker-compose elige el comando de cada servicio)
FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# Primero dependencias (capa cacheable), luego el codigo
COPY pyproject.toml uv.lock* ./
RUN uv sync --no-install-project

COPY app ./app
COPY frontend ./frontend
COPY models ./models
COPY scripts ./scripts

ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
