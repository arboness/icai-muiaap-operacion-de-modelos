## Explicación

- Con pydantic, se ha realizado un contrato de entrada de datos para que, antes de probar un modelo, comprobar que los datos que se pasan siguen la estructura que el modelo espera. Como no sé qué rangos son los correctos, he puesto algunos valores por decisión propia pero que acepten los datos del csv. 

- El contrato se encuentra en el archivo ``src/semana3/contract.py``. 

- Para probarlo, se debe de ejecutar el archivo ``src/semana3/contract_test.py`` con ``uv run python -m semana3.contract_test``.

### Tarea 1
### Clasifica las piezas - Separa datos historicos de entrenamiento, artefacto entregado y datos nuevos de inferencia. Justifica que recibe cada frontera.
Aún no tenemos el artefacto entregado (modelo .joblib), luego tampoco los datos nuevos de inferencia fruto de aplicar el modelo a los datos históricos.

- **Datos históricos de entrenamiento:** No los tenemos.
- **Artefacto entregado:** ``.joblib``, no lo tenemos.
- **Datos nuevos de inferencia:** Tampoco se tienen.

### Tarea 2

```python
# src/semana3/contract.py

class WineInputSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")
     
    fixed_acidity: float = Field(...,ge=0,le=20, description="Fixed acidity of the wine sample")
    volatile_acidity: float = Field(...,ge=0, le=2, description="Volatile acidity of the wine sample")
    citric_acid: float = Field(...,ge=0, le=2, description="Citric acid of the wine sample")
    residual_sugar: float = Field(...,ge=0,le=20, description="Residual sugar of the wine sample")
    chlorides: float = Field(...,ge=0, le=1, description="Chlorides of the wine sample")
    free_sulfur_dioxide: float = Field(..., ge=0, le=100, description="Free sulfur dioxide of the wine sample")
    total_sulfur_dioxide: float = Field(..., ge=0, le=300, description="Total sulfur dioxide of the wine sample")
    density: float = Field(..., ge=0.98, le=1.01, description="Density of the wine sample")
    ph: float = Field(..., ge=2.5, le=4.5, description="pH of the wine sample")
    sulphates: float = Field(..., ge=0, le=3, description="Sulphates of the wine sample")
    alcohol: float = Field(..., ge=5, le=20, description="Alcohol content of the wine sample")
```

### Tarea 3
Como Pydantic **ignora el orden de las columnas**, si no definimos ``FEATURES_NAME``, puede ser que nuestro ``df`` tenga la mismas columnas pero en distinto orden, y que el modelo reciba por ejemplo ``free_sulfur_dioxide`` en el lugar de ``total_sulfur_dioxide`` y viceversa y que prediga erróneamente teniendo en cuenta el valor de ``total_sulfur_dioxide`` para ``free_sulfur_dioxide`` y viceversa.

```python 
# src/semana3/contract_test.py
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
```

### Tarea 4 
#### Diseña fallos - Propone una fila valida, una columna desconocida, una fila fuera de rango y el momento del flujo en el que cada una debe fallar.
```python
    # src/semana3/contract_test.py

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
        

    # Lanza ValidationError y falla si no se captura
    wine_schema_sample = schema_row(**invalid_row)
              
    # Lanza ValidationError y falla si no se captura
    wine_schema_sample = schema_row(**unknown_column_row)          
    

```

### Tarea 5
#### Define aceptacion - Escribe tres criterios que el modulo de la clase 2 debera demostrar con tests y con un comando local.
- **Criterio 1: Un CSV válido produce una predicción por fila.**
  - **Test:** con un CSV de 3 filas válidas, la salida tiene 3 predicciones en el mismo orden.
  - **Comando:** uv run python -m semana3.cli predict inference_samples.csv, genera el fichero de salida sin errores.  
- **Criterio 2: Una fila inválida hace fallar la ejecución sin dejar salida parcial.**
  - **Test:** con un CSV que incluye fixed_acidity=100, se lanza el error esperado y no se crea el fichero de predicciones.
  - **Comando:** ejecutar la CLI con un CSV malo, implica código de salida distinto de 0, mensaje que indica fila y campo, y ningún fichero escrito. 
- **Criterio 3: El orden de las columnas de entrada no afecta a la predicción**.
  - **Test:**  el mismo CSV con dos columnas intercambiadas da exactamente las mismas predicciones (porque el módulo reordena según el contrato antes de llamar al modelo).
  - **Comando:** ejecutar la CLI con ambos CSV y comparar las salidas.


## Conclusión

Un contrato de datos es necesario ya que, si queremos que nuestro modelo le funcione a más personas, los datos que introducen esas personas deben de coincidir con los datos con los que fue entrenado el modelo. **No se puede entrenar un modelo con peras y después probarlo con manzanas.**

