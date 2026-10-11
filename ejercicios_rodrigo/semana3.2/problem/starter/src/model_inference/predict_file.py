"""TODO: script CLI que encadena contratos, preprocesado e inferencia."""

from model_inference.constants import DEFAULT_MODEL_PATH
import pandas as pd
import os
from pathlib import Path
from model_inference.inference import infer_wine_quality, load_feature_names, load_model, load_wine_quality_model, load_wine_quality_model_version, preprocess, preprocessOutput
from model_inference.preprocess import FEATURE_NAMES, MODEL_VERSION, preprocess_wine_request

# Implementa el comando:
# python -m model_inference.predict_file --input <csv> --output <csv>
# No dejes un archivo de salida parcial si alguna fila es inválida.



BASE_DIR = Path(os.getcwd())

def predict_file(input_path, output_path):
    
    df = pd.read_csv(BASE_DIR / input_path)
    df_predictions = df.copy()
    model = load_model(DEFAULT_MODEL_PATH)
    feature_names = load_feature_names(model)
    estimator = load_wine_quality_model(model)
    model_version = load_wine_quality_model_version(model)
    predicciones = []

    if feature_names != FEATURE_NAMES:
        raise ValueError(f"error: El modelo espera unas características diferentes. \nCaracterísticas esperadas por el modelo: {feature_names} \nCaracterísticas recibidas: {FEATURE_NAMES}.")
    elif estimator == None:
        raise ValueError(f"error: No hay ningún modelo en el artefacto.")
    elif MODEL_VERSION != model_version:
        raise ValueError(f"error: El modelo espera una versión diferente. \nVersión esperada del modelo: {model_version} \nVersión recibida: {MODEL_VERSION}.")
    else:
        for i, row in df_predictions.iterrows():
            try:
                verified_row = preprocess(row)
            except ValueError as e:
                raise ValueError(f"{e}")
 
            verified_vector = preprocess_wine_request(verified_row)
            prediction = infer_wine_quality(row = verified_vector, model = estimator)
            try:
                valid_prediction = preprocessOutput(prediction[0])
            except ValueError as e:
                raise ValueError(f"{e}")
    
            predicciones.append(valid_prediction.wine_quality)
                
   
        df_predictions["predictions"] = predicciones
        df_predictions.to_csv(output_path, index=False)
        
