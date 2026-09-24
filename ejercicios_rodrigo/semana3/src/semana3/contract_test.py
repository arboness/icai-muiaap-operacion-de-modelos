import pandas as pd
from pydantic import ValidationError, warnings
from pydantic import ValidationError
from semana3.contract import WineInputSchema

DATASET = "inference_samples.csv"

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
        valid.append(WineInputSchema(**row))
    except ValidationError as e:
        invalid.append({"row": i, "errors": e.errors()})    

print(valid) 
        