# Readme de explicación de las soluciones de la semana 4
## Ejercicio 1
### 01 Clasifica el contenido - Asigna cada dato a model.joblib, manifest.json o codigo: estimador, versiones nombres, etiquetas y reglas.
| Elemento | ¿Dónde vive? | ¿Qué riesgo evita? |
| --- | --- | --- |
| Estimador entrenado | **model.joblib** | Tener un modelo distinto al validado |
| Versión del esquema | **En el manifest.json** | Contratos de entrada/salida incompatibles |
| Orden y nombres de features | **En el manifest.json** | Features erróneas o desordenadas sin error visible |
| Versión del preprocesado | **En el manifest.json** | Para que el preprocesado con el que fue entrenado el modelo sea el mismo que apliquemos nosotros |
| Etiquetas de salida permitidas | **En el manifest.json** | Clases inesperadas o mal mapeadas |
| Versión del modelo | **En el manifest.json** | Falta de trazabilidad |
| Tipo de estimador | **En el manifest.json** | Cargar el artefacto equivocado |

### 02 Completa el manifiesto - Propone schema_version, model_version, preprocessing_version, feature_names,output_labels y estimator_type.
```json
{
    "schema_version": "v1.0",
    "model_version": "wine-quality-rf-v1",
    "preprocess_version": "v1.0",
    "features_name": [
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
    ],
    "output_labels": [
        "acceptable",
        "excellent",
        "needs_review"
    ],
    "estimator_type": {
        "RandomForestClassifier": {
            "class_weight": "balanced_subsample",
            "max_depth": 8,
            "min_samples_leaf": 2,
            "n_estimators": 200,
            "random_state": 42
        }
    }
}
```


03 Escribe invariantes - Define al menos tres condiciones que deben bloquear la carga o la inferencia antes de
escribir resultados.

```python
assert set(manifest_draft) == required_keys
assert len(manifest_draft["feature_names"]) == 11
assert "sample_id" not in manifest_draft["feature_names"]
```

04 Rompe el contrato - Altera orden de columnas, version de preprocesado, etiqueta de salida y tipo de
estimador; predice el error y su etapa.
```python

wrong_feature_names = [
    "fixed_acidity",
    "chlorides",
    "free_sulfur_dioxide",
    "total_sulfur_dioxide",
    "density",
    "volatile_acidity",
    "citric_acid",
    "residual_sugar",
    "ph",
    "sulphates",
    "alcohol",
]

wrong_estimator_type={
"RandomForestClassifier": {
        "class_weight": "balanced_subsample",
        "max_depth": 10,
        "min_samples_leaf": 2,
        "n_estimators": 200,
        "random_state": 42
    }
}

wrong_manifest_draft = {
    "schema_version": "v1.0",
    "model_version": legacy_model_version,
    "preprocessing_version": "v2.0",
    "feature_names": wrong_feature_names,
    "output_labels": ["low", "medium", "high"],
    "estimator_type": wrong_estimator_type,
}

```

| Cambio | Frontera que debe rechazarlo | Mensaje útil esperado | ¿Se escribe CSV? |
| --- | --- | --- | --- |
| Se intercambian `density` y `alcohol` | Validación de entrada | "Orden de features no coincide con el manifest" | No |
| Cambia `preprocessing_version` | Carga del artefacto | "preprocessing_version incompatible" | No |
| El modelo devuelve `unknown` | Validación de salida | "Etiqueta 'unknown' no permitida" | No |
| La petición incluye `ph = 99` | Validación de entrada | "ph=99 fuera de rango [5,20 ]" | No |

### 05 Decide la politica de filas - Explica
Las filas del csv solo se escribirán una vez validado y predecido todo. Cuando se ha valiado el artefacto y el model.joblib y se han comprobado todos los campos, podemos empezar a procesar las filas para predecir sobre ellas de una en una. Después, una por una se valida la salida del modelo con el contrato de salida y se apenda a la lista de filas válidas. Si se han procesado todas las filas correctamente, se escriben en un archivo de salida, si no, el programa ha fallado en algún momento y no se ha llegado hasta aquí. De esta manera no se deja un csv de salida parcial.

## Ejercicio 2
### 01 Implementa el manifiesto - Completa ArtifactManifest y create_manifest con campos estrictos, versiones, orden y etiquetas.
Primero cargo el manifiesto, valido con las condiciones del contrato, y después, con ``field_validator``, aseguro que recibo lo que espero, si no, ``ValueError``.

```python

# scr\model_packaging\artifact.py
class ArtifactManifest(BaseModel):
    """TODO: declara y valida los metadatos del bundle."""

    model_config = ConfigDict(extra="forbid")

    schema_version: str = Field(min_length=1)
    model_version: str = Field(min_length=1)
    preprocessing_version: str = Field(min_length=1)
    feature_names: tuple[str, ...] = Field(min_length=1)
    output_labels: tuple[QualityBand, ...] = Field(min_length=1)
    estimator_type: str = Field(min_length=1)

    
    @field_validator("schema_version")
    @classmethod
    def validate_schemaversion(cls, value):
        if value != SCHEMA_VERSION:
            raise ValueError(f"La versión del esquema recibida {value} no es la esperada. Se esperaba {SCHEMA_VERSION}")

        return value
    
    @field_validator("preprocessing_version")
    @classmethod
    def validate_preprocessing_version(cls, value):
        if value != PREPROCESSING_VERSION:
            raise ValueError(f"La versión del preprocesado recibida {value} no es la esperada. Se esperaba {PREPROCESSING_VERSION}")

        return value
    
    @field_validator("feature_names")
    @classmethod
    def validate_feature_names(cls, value):
        if value != FEATURE_NAMES:
            raise ValueError(f"Las features recibidas {value} no son las esperadas. Se esperaba {FEATURE_NAMES}")

        return value
    
    @field_validator("output_labels")
    @classmethod
    def validate_output_labels(cls, value):
        if value != OUTPUT_LABELS:
            raise ValueError(f"Las etiquetas de salida recibidas {value} no son las esperadas. Se esperaba {OUTPUT_LABELS}")

        return value
```

Para crear el manifiesto, le paso el objeto ``WineQualityEstimator`` y la versión del modelo. Se comprueban todos los campos con el contrato ``ArtifactManifest`` de pydantic.

```python
# scr\model_packaging\artifact.py
def create_manifest(
    estimator: WineQualityEstimator, model_version: str
) -> ArtifactManifest:
    """devuelve un manifiesto compatible con el contrato."""
    return ArtifactManifest(
        schema_version=SCHEMA_VERSION,
        model_version=model_version,
        preprocessing_version=PREPROCESSING_VERSION,
        feature_names=FEATURE_NAMES,
        output_labels=OUTPUT_LABELS,
        estimator_type=type(estimator).__name__,
        
    )
```

### 02 Implementa el guardado - Escribe manifest.json y model.joblib de forma reproducible y valida la interfaz del estimador.

```python
# scr\model_packaging\artifact.py
def save_model_bundle(
    bundle_path: Path,
    estimator: WineQualityEstimator,
    manifest: ArtifactManifest | None = None,
) -> ArtifactManifest:
    """TODO: escribe manifest.json y model.joblib de forma segura."""

    if manifest is None:
        manifest = create_manifest(estimator, MODEL_VERSION)

    bundle_path.mkdir(parents=True, exist_ok=True)

    with open(bundle_path / MANIFEST_FILENAME, "w", encoding="utf-8") as f:
        json.dump(manifest.model_dump(mode="json"), f, indent=4, ensure_ascii=False)

    joblib.dump(estimator, bundle_path / MODEL_FILENAME)

    return manifest
```

### 03 Implementa la carga - Rechaza archivos ausentes, JSON incompatible y estimadores no compatibles antes de inferir.
Cargo el manifiesto y el estimador. Valido el manifiesto, y una vez validado, cargo el estimador del joblib.

```python
# scr\model_packaging\artifact.py
def load_model_bundle(bundle_path: Path) -> LoadedModelBundle | None:
    """TODO: valida el manifiesto antes de cargar el estimador."""
    
    manifest_path = bundle_path / MANIFEST_FILENAME
    estimator_path = bundle_path / MODEL_FILENAME
    
    if not manifest_path.exists():
        raise FileNotFoundError(f"El archivo {manifest_path} no existe.")
    
    if not estimator_path.exists():
        raise FileNotFoundError(f"El archivo {estimator_path} no existe.")
    
    with open(manifest_path, 'r') as f:
        manifest = json.load(f)
    
    validated_manifest = ArtifactManifest.model_validate(manifest)
        
    estimator = joblib.load(estimator_path)
    
    return LoadedModelBundle(estimator=estimator, manifest=validated_manifest)

```

### 04 Valida la salida - Completa infer_wine_quality y exige etiqueta, confianza, modelo y preprocesado validos.
Dado un objeto ``WineQualityRequest``, predigo sobre los datos, construyo la salida y verifico que cumple el contrato de salida. Devuelvo un objeto del contrato de salida.

```python
def infer_wine_quality(
    bundle: LoadedModelBundle,
    request: WineQualityRequest,
) -> WineQualityPrediction:
    """TODO: preprocesa, invoca el estimador y valida la respuesta."""

    features = preprocess_wine_request(request).as_vector()

    label = bundle.estimator.predict([features])[0]
    probabilities = bundle.estimator.predict_proba([features])[0]

    return WineQualityPrediction(
        quality_band=str(label),
        confidence=float(max(probabilities)),
        model_version=bundle.manifest.model_version,
        preprocessing_version=bundle.manifest.preprocessing_version,
    )
```

### 05 Completa el CLI - Lee, valida e infiere todas las filas; abre la salida solo al final y conserva el esquema estable.
Leo el csv, lo almaceno en filas, retiro el ``sample_id`` ya que no está en el contrato de entrada ni de salida para poder apendarlo después. Predigo sobre cada fila una vez pasado el contrato, guardo la predicción que ha pasado el contrato de salida, y si todo ha ido bien, vuelco la salida en un csv.
El programa termina con el número de filas leídas.

```python
def predict_file(
    input_path: Path,
    output_path: Path,
    bundle_path: Path,
) -> int:
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
        for sample_id, prediction in zip(sample_ids, predictions):
            writer.writerow({"sample_id": sample_id, **prediction.model_dump()})

    return len(predictions)
```

### Ejecución

```bash
# Todo correcto  tmp/pred_ok.csv
uv run python -m model_packaging.predict_file --input assets/data/inference_samples.csv --output tmp/pred_ok.csv --bundle assets/models/bundle_ok

```

```bash
# Manifest corrupto
uv run python -m model_packaging.predict_file --input assets/data/inference_samples.csv --output tmp/pred_manifest_corrupto.csv --bundle assets/models/bundle_corrupto
```

```bash
# Datos corruptos, sin fichero de salida
uv run python -m model_packaging.predict_file --input assets/data/inference_samples_corrupted.csv --output tmp/pred_datos_corruptos.csv --bundle assets/models/bundle_ok
```