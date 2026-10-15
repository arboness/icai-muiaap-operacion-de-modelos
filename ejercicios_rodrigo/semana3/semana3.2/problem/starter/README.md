# Ejercicio 2 

- Con pydantic, se ha realizado un contrato de entrada de datos para que, antes de probar un modelo, comprobar que los datos que se pasan siguen la estructura que el modelo espera. Además, se ha cargado un ``.joblib`` que se ha proporcionado para el ejercicio.


- Para probarlo, se debe de ejecutar:
```bash 
uv run python -m model_inference.predict_file.py --input assets/inference_incorrect_samples.csv --output temp/predictions.csv
```

- En el punto 6, se definen las instrucciones para comprobar los "tests" manuales que se piden en el enunciado.

## 01 - Lee la especificacion - Ejecuta la suite roja y convierte cada nombre de test en una regla de la API local.
```bash 
uv run pytest
```

## 02 - Completa request y prediction con Pydantic; rechaza extras, tipos imposibles y valores fuera de rango

```python
# src/model_inference/contract.py
WineQualityLabel = Literal["Buena", "Mala"]

class WineQualityRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
     
    fixed_acidity: float = Field(ge=0,le=20, description="Fixed acidity of the wine sample")
    volatile_acidity: float = Field(ge=0, le=2, description="Volatile acidity of the wine sample")
    citric_acid: float = Field(ge=0, le=2, description="Citric acid of the wine sample")
    residual_sugar: float = Field(ge=0,le=20, description="Residual sugar of the wine sample")
    chlorides: float = Field(ge=0, le=1, description="Chlorides of the wine sample")
    free_sulfur_dioxide: float = Field(ge=0, le=100, description="Free sulfur dioxide of the wine sample")
    total_sulfur_dioxide: float = Field(ge=0, le=300, description="Total sulfur dioxide of the wine sample")
    density: float = Field(ge=0.98, le=1.01, description="Density of the wine sample")
    ph: float = Field(ge=2.5, le=4.5, description="pH of the wine sample")
    sulphates: float = Field(ge=0, le=3, description="Sulphates of the wine sample")
    alcohol: float = Field(ge=5, le=20, description="Alcohol content of the wine sample")
    
class WineQualityPrediction(BaseModel):
    model_config = ConfigDict(extra="forbid")
    
    sample_id: str = Field(min_length=1)
    quality_band: WineQualityLabel = Field()
    confidence: float = Field(ge=0, le=1)
    model_version: str = Field(min_length=1)
    preprocessing_version: str = Field(min_length=1)
```

## 03 - Implementa preprocesado - Construye un vector estable con las once features y una version explicita; no mezcles sample_id

```python 
# src/model_inference/preprocess.py
MODEL_VERSION = "wine-quality-rf-v1"

FEATURE_NAMES = [
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
    "alcohol",
]

@dataclass(frozen=True, slots=True)
class WineFeatures:
    fixed_acidity: float
    volatile_acidity: float
    citric_acid: float
    residual_sugar: float
    chlorides: float
    free_sulfur_dioxide: float
    total_sulfur_dioxide: float
    density: float
    ph: float
    sulphates: float
    alcohol: float

    def as_vector(self):
        return [getattr(self, name) for name in FEATURE_NAMES]


def preprocess_wine_request(request):
    data = request.model_dump()
    return WineFeatures(**{name: data[name] for name in FEATURE_NAMES})
```

## 04 - Implementa carga e inferencia - Valida el payload del artefacto antes de invocar predict/predict_proba y valida la salida resultante.
```text
# src/model_inference/inference.py
load_wine_quality_model, infer_wine_quality.    
```
```python
# src/model_inference/predict_file.py
    prediction = WineQualityPrediction(
        sample_id=sample_id,
        quality_band=band,
        confidence=confidence,
        model_version=model_version,
        preprocessing_version=PREPROCESS_VERSION,
    )
```

## 05 - Completa el CLI - Lee todas las filas, acumula predicciones y escribe el CSV solo cuando el conjunto es valido.
```python
# src/model_inference/predict_file.py

```


## 06 - Amplia los errores - Prueba columna extra, segunda fila invalida y artefacto incompatible; confirma que no queda CSV parcial.

### Probar con columna extra (Fallo del contrato)
```bash
uv run python -m model_inference.predict_file --input assets/inference_incorrect_columns.csv --output temp/predictions.csv

```
### Probar con valores erróneos (Fallo del contrato)
```bash
uv run python -m model_inference.predict_file --input assets/inference_incorrect_samples.csv --output temp/predictions.csv

```

### artefacto incompatible. 
Cambiar ``MODEL_VERSION = "wine-quality-rf-v1"`` en ``src/model_inference/preprocess.py``.

```python
# src/model_inference/preprocess.py
MODEL_VERSION = "wine-quality-rf-error"
```

```bash
uv run python -m model_inference.predict_file --input assets/inference_samples.csv --output temp/predictions.csv
```


