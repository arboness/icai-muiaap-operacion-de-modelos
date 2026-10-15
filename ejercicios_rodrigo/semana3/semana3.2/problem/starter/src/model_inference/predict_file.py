"""TODO: script CLI que encadena contratos, preprocesado e inferencia."""
import argparse
import os
from pathlib import Path
import sys

import pandas as pd
from pydantic import ValidationError

from model_inference.contracts import WineQualityPrediction, WineQualityRequest
from model_inference.inference import DEFAULT_MODEL_PATH, infer_wine_quality, load_wine_quality_model
from model_inference.preprocess import FEATURE_NAMES, PREPROCESS_VERSION, preprocess_wine_request

# Implementa el comando:
# python -m model_inference.predict_file --input <csv> --output <csv>
# No dejes un archivo de salida parcial si alguna fila es inválida.



BASE_DIR = Path(os.getcwd())


def predict_file(input_path, output_path, model_path):
    estimator, model_version = load_wine_quality_model(model_path)  

   
    df = pd.read_csv(input_path, dtype=str, keep_default_na=False)

    results = []
    for _, row in df.iterrows():
        sample_id = row.get("sample_id", "")
        data = row.drop("sample_id", errors="ignore").to_dict()
        try:
            request = WineQualityRequest.model_validate(data)
            features = preprocess_wine_request(request)
            band, confidence = infer_wine_quality(features, estimator)
            prediction = WineQualityPrediction(
                sample_id=sample_id,
                quality_band=band,
                confidence=confidence,
                model_version=model_version,
                preprocessing_version=PREPROCESS_VERSION,
            )
        except ValidationError as e:
            raise ValueError(f"Fila {sample_id!r} inválida:\n{e}") from e
        results.append(prediction.model_dump())
    
    columns = list(WineQualityPrediction.model_fields)
    pd.DataFrame(results, columns=columns).to_csv(output_path, index=False)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Predice la calidad del vino desde un CSV")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--model", default=DEFAULT_MODEL_PATH)
    args = parser.parse_args(argv)
    try:
        predict_file(args.input, args.output, args.model)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return 2


if __name__ == "__main__":
    sys.exit(main())