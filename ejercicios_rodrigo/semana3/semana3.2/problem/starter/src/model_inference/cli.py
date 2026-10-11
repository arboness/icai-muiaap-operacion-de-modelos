import argparse
from pathlib import Path
from model_inference.predict_file import predict_file


def main():
    parser = argparse.ArgumentParser(description="Predice la calidad de vinos a partir de un CSV.")
    parser.add_argument("--input", type=Path, required=True, help="CSV de entrada con las muestras")
    parser.add_argument("--output", type=Path, required=True, help="CSV de salida con las predicciones")
    args = parser.parse_args()
    
    try:
        predict_file(args.input, args.output)
    except ValueError as e:
        print(f"{e}")
        return 2
    
if __name__ == "__main__":
    main()