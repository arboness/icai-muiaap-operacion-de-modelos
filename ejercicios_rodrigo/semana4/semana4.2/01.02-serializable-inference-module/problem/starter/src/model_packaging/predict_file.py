"""Punto de extensión del CLI de inferencia sobre un bundle."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

from model_packaging.artifact import infer_wine_quality, load_model_bundle, DEFAULT_BUNDLE_PATH
from model_packaging.contracts import WineQualityPrediction, WineQualityRequest



def predict_file(
    input_path: Path,
    output_path: Path,
    bundle_path: Path,
) -> int:
    """Valida todas las filas y escribe el CSV solo al final."""

    bundle = load_model_bundle(bundle_path)

    with open(input_path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    sample_ids = []
    predictions = []
    for row in rows:
        sample_ids.append(row.pop("sample_id"))
        request = WineQualityRequest.model_validate(row)
        predictions.append(infer_wine_quality(bundle, request))

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        fieldnames = ["sample_id", *WineQualityPrediction.model_fields]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for sample_id, prediction in zip(sample_ids, predictions, strict=True):
            writer.writerow({"sample_id": sample_id, **prediction.model_dump()})

    return len(predictions)


def parse_args() -> argparse.Namespace:
    """Declara la interfaz del comando público."""

    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--bundle", default=DEFAULT_BUNDLE_PATH, type=Path)
    return parser.parse_args()


if __name__ == "__main__":
    arguments = parse_args()
    rows_predicted = predict_file(
        input_path=arguments.input,
        output_path=arguments.output,
        bundle_path=arguments.bundle,
    )
    print(f"{rows_predicted} predicciones escritas en {arguments.output}")
    raise SystemExit(0)