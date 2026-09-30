"""TODO: script CLI que encadena contratos, preprocesado e inferencia."""
import argparse

import pandas as pd
import os
from pathlib import Path
import joblib
import numpy as np
from model_inference.inference import build_feature_vector, infer_wine_quality, load_feature_names, load_wine_quality_model, load_wine_quality_model_version, preprocessInput, preprocessOutput
from model_inference.preprocess import FEATURE_NAMES, MODEL_VERSION
# Implementa el comando:
# python -m model_inference.predict_file --input <csv> --output <csv>
# No dejes un archivo de salida parcial si alguna fila es inválida.


BASE_DIR = Path(os.getcwd())


parser = argparse.ArgumentParser(description="Predice la calidad de vinos a partir de un CSV.")
parser.add_argument("--input", type=Path, required=True, help="CSV de entrada con las muestras")
parser.add_argument("--output", type=Path, required=True, help="CSV de salida con las predicciones")
args = parser.parse_args()

##predictions = model.predict(valid_df)  
#print(predictions)        

def main():
    df = pd.read_csv(BASE_DIR / "assets" / args.input)

    feature_names = load_feature_names()
    estimator = load_wine_quality_model()
    model_version = load_wine_quality_model_version()
    predicciones = []
    error = False

    print(estimator)
    if feature_names == None or feature_names != FEATURE_NAMES:
        print(f"error: El modelo espera unas características diferentes. \nCaracterísticas esperadas: {feature_names} \nCaracterísticas recibidas: {FEATURE_NAMES}.")
    elif estimator == None:
        print(f"error: No hay ningún modelo en el artefacto.")
    elif MODEL_VERSION != model_version:
        print(f"error: El modelo espera una versión diferente. \nVersión esperada: {model_version} \nVersión recibida: {MODEL_VERSION}.")
    else:
        for i, row in df.iterrows():
            modified_row = row[FEATURE_NAMES]
            valid_row = preprocessInput(modified_row)

            if valid_row is None:
                print(f"El conjunto de datos no es válido. Error al procesar la fila {i}. ")
                error = True 
                break   
            vector = build_feature_vector(valid_row) 
            prediction = infer_wine_quality(row = vector, model = estimator)
            valid_prediction = preprocessOutput(prediction[0])
            
            if  valid_prediction == None:
                print(f"La predicción no es válida. Error al predecir la fila {i}. ")
                error = True 
                break   
    
            predicciones.append(valid_prediction.wine_quality)
                
            
        if not error:       
            df["predictions"] = predicciones
            df.to_csv(args.output, index=False)
        
if __name__ == "__main__":
    main()