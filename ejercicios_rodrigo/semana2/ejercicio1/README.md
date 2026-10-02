## Creación de proyecto con uv 
1. Una vez descargado, situarse en la raíz del proyecto y ejecutar ``uv sync`` parea sincronizar dependencias.
2. Probar con:
   1. ``APP_ENV=dev uv run python -m env_demo.main``
   2. ``APP_ENV=pre uv run python -m env_demo.main``
   3. ``APP_ENV=pro uv run python -m env_demo.main``
3. Seguir con ``uv run pytest`` y ``uv run ruff check``.