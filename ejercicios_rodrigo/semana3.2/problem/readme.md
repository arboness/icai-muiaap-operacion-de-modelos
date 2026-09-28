# Problema — Construir un módulo local de inferencia

Trabajad únicamente en `starter/`; esa carpeta es el proyecto que recibe el
alumnado. El artefacto preentrenado se entrega aparte como
`models/wine_quality_classifier.joblib`.

```bash
cd starter
uv sync
uv run pytest
```

Las pruebas empezarán rojas. Implementad los archivos en este orden:

1. `contracts.py`: petición validada y predicción de salida.
2. `preprocess.py`: vector con las 11 características en orden estable.
3. `inference.py`: carga y validación del artefacto, más predicción.
4. `predict_file.py`: entrada CSV, cadena de inferencia y CSV de salida.

El `.joblib` contiene un diccionario con `estimator`, `feature_names` y
`model_version`. El cargador debe comprobar que `feature_names` coincide con
`FEATURE_NAMES` antes de hacer una predicción.

El comando final debe ser:

```bash
uv run python -m model_inference.predict_file \
  --input assets/inference_samples.csv \
  --output .tmp/wine_predictions.csv
```

No consultéis la carpeta `solutions/` hasta el debrief.
