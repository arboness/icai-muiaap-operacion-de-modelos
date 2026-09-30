"""TODO: carga del .joblib e inferencia sobre características preparadas."""

# Declara DEFAULT_MODEL_PATH, load_wine_quality_model() e infer_wine_quality().
# Comprueba las características del artefacto antes de llamar al clasificador.
import logging
from pathlib import Path
from model_inference.contracts import WineInputSchema, WineQualityPredictionOutputSchema
from model_inference.preprocess import FEATURE_NAMES
from model_inference.constants import DEFAULT_MODEL_PATH
from pydantic import ValidationError
import joblib
import numpy as np




logging.basicConfig(
    filename="errores.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def load_feature_names():
    return joblib.load(DEFAULT_MODEL_PATH).get("feature_names")

def load_wine_quality_model():
    return joblib.load(DEFAULT_MODEL_PATH).get("estimator")
 
def load_wine_quality_model_version():
    return joblib.load(DEFAULT_MODEL_PATH).get("model_version")

def infer_wine_quality(row, model):
    return model.predict(np.array(row).reshape(1, -1))

def build_feature_vector(features):
    return [float(getattr(features, name)) for name in FEATURE_NAMES]

def preprocessInput(row):
    try:
        return WineInputSchema.model_validate(row.to_dict())
    except ValidationError as e:
        logger.error(f"Fila inválida: {e.errors()}")
        return None

def preprocessOutput(prediction):
    try:
        validPrediction = WineQualityPredictionOutputSchema.model_validate({"wine_quality": str(prediction)})
        return validPrediction
    except ValidationError as e:
        logger.error(f"Predicción inválida: {e.errors()}")
        return None  