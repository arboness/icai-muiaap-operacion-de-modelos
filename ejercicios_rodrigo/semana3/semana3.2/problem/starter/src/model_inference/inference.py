"""TODO: carga del .joblib e inferencia sobre características preparadas."""

# Declara DEFAULT_MODEL_PATH, load_wine_quality_model() e infer_wine_quality().
# Comprueba las características del artefacto antes de llamar al clasificador.

from pathlib import Path
from model_inference.preprocess import FEATURE_NAMES, MODEL_VERSION
import joblib


DEFAULT_MODEL_PATH = Path("models/wine_quality_classifier.joblib")


def load_wine_quality_model(path=DEFAULT_MODEL_PATH):
    try:
        artifact = joblib.load(path)
    except FileNotFoundError as e:
        raise ValueError(f"No existe el modelo: {path}") from e

    if not isinstance(artifact, dict):
        raise ValueError("El artefacto no tiene el formato esperado")

    estimator = artifact.get("estimator")
    if not (hasattr(estimator, "predict") and hasattr(estimator, "predict_proba")):
        raise ValueError("El artefacto no contiene un clasificador compatible")

    missing = {"feature_names", "model_version"} - artifact.keys()
    if missing:
        raise ValueError(f"Al artefacto le faltan claves: {sorted(missing)}")

    if list(artifact["feature_names"]) != list(FEATURE_NAMES):
        raise ValueError(
            f"feature_names incompatibles.\n"
            f"Modelo: {artifact['feature_names']}\nContrato: {FEATURE_NAMES}"
        )

    if artifact["model_version"] != MODEL_VERSION:
        raise ValueError(
            f"Versión incompatible: modelo {artifact['model_version']}, esperada {MODEL_VERSION}"
        )

    return estimator, artifact["model_version"]

def infer_wine_quality(features, estimator):
    vector = [features.as_vector()]
    band = estimator.predict(vector)[0]
    confidence = float(estimator.predict_proba(vector)[0].max())
    return str(band), confidence