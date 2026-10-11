"""TODO: carga del .joblib e inferencia sobre características preparadas."""

# Declara DEFAULT_MODEL_PATH, load_wine_quality_model() e infer_wine_quality().
# Comprueba las características del artefacto antes de llamar al clasificador.
import logging
from pathlib import Path
from model_inference.contracts import WineQualityRequest, WineQualityPrediction
from model_inference.preprocess import FEATURE_NAMES
from pydantic import ValidationError
import joblib
import numpy as np

## Como estoy revisando esto después de haber visto ya otros ejercicios en clase con función de cargade modelo, creo esta función para cargarlo una sola vez
def load_model(path):
    return joblib.load(path)

def load_feature_names(model):
    return model["feature_names"]

def load_wine_quality_model(model):
    return model["estimator"]
 
def load_wine_quality_model_version(model):
    return model["model_version"]

def infer_wine_quality(row, model):
    return model.predict([row])

def preprocess(row) -> WineQualityRequest:
    try:
        return WineQualityRequest.model_validate(row.to_dict())
    except ValidationError as e:
        raise ValueError(f"Error al procesar la fila: {row}. Error: {e}")

def preprocessOutput(prediction):
    try:
        validPrediction = WineQualityPrediction.model_validate({"wine_quality": str(prediction)})
        return validPrediction
    except ValidationError as e:
        raise ValueError(f"Predicción inválida: {e}")