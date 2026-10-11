import pandas as pd
from pydantic import ValidationError
import warnings
from pydantic import ValidationError
from semana3.contract import WineInputSchema

DATASET = "inference_samples.csv"

# Tarea 3
# Como Pydantic ignora el orden de las columnas, si no definimos FEATURES_NAME, puede ser que nuestro df tenga la mismas columnas
# pero en distinto orden, y que el modelo reciba por ejemplo free_sulfur_dioxide en el lugar de total_sulfur_dioxide y viceversa y que
# prediga erróneamente teniendo en cuenta el valor de total_sulfur_dioxide para free_sulfur_dioxide y viceversa.
FEATURES_NAME = [
    "fixed_acidity",
    "volatile_acidity",
    "citric_acid",
    "residual_sugar",
    "chlorides",
    "free_sulfur_dioxide",
    "total_sulfur_dioxide",
    "density",
    "ph", 
    "sulphates",
    "alcohol"
]


def schema_row(dict_row)-> WineInputSchema | None:
    try:
        return  WineInputSchema(**dict_row)
    except ValidationError as e:
        return None

def main():
    invalid_row = {
        "fixed_acidity": 100,
        "volatile_acidity": 0.70,
        "citric_acid": 0.0,
        "residual_sugar": 1.9,
        "chlorides": 0.076,
        "free_sulfur_dioxide": 11.0,
        "total_sulfur_dioxide": 34.0,
        "density": 0.9978,
        "ph": 3.51,
        "sulphates": 0.56,
        "alcohol": 9.4,
    }
    
    unknown_column_row = {
        "fixed_acidity": 100,
        "volatile_acidity": 0.70,
        "citric_acid": 0.0,
        "residual_sugar": 1.9,
        "chlorides": 0.076,
        "free_sulfur_dioxide": 11.0,
        "total_sulfur_dioxide": 34.0,
        "density": 0.9978,
        "ph": 3.51,
        "sulphates": 0.56,
        "alcohol": 9.4,
        "unknown": 3
    }
    
    df = pd.read_csv(DATASET)

    expected = set(WineInputSchema.model_fields)
    missing = expected - set(df.columns)
    extra = set(df.columns) - expected

    if missing:
        
        raise ValueError(f"Faltan columnas obligatorias: {sorted(missing)}")

    if extra:
        warnings.warn(f"Se ignoran columnas no esperadas: {sorted(extra)}")
        df = df[list(expected)]

    valid, invalid = [], []
         
    for i, row in enumerate(df.to_dict(orient="records")):
        try:
            wine_schema_sample = schema_row(row)
            valid.append(row)
        except ValidationError as e:
            invalid.append(row)
            warnings.warn(f"Fallo de validación: {e}")   

    # tarea 4, lanza ValidationError y falla si no se captura
    try:
        wine_schema_sample = schema_row(invalid_row)
    except ValidationError as e:
        warnings.warn(f"Fallo de validación: {e}")      
         
    # tarea 4, lanza ValidationError y falla si no se captura     
    try:
        wine_schema_sample = schema_row(unknown_column_row)
    except ValidationError as e:
        warnings.warn(f"Fallo de validación: {e}")             

if __name__ == "__main__":
    main()    