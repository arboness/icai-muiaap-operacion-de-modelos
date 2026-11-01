# Readme de explicación de las soluciones de la semana 5
 
## Ejercicio 2

### 01 Localiza y valida el bundle - Define MODEL_UI_BUNDLE y verifica que el directorio real contiene manifest.json y model.joblib.

Antes de arrancar compruebo que el directorio existe y que contiene los dos artefactos del contrato de S4: ``manifest.json`` y ``model.joblib``.

```bash
export MODEL_UI_BUNDLE="assets/model/bundle"
```

### 02 Construye los widgets - Implementa collect_values() generando los once widgets desde FIELD_SPECS, sin cambiar nombres, orden ni límites.

Por cada ``FieldSpec`` creo un ``st.number_input`` con:
- ``label`` → la etiqueta en español que ve el usuario.
- ``min_value``, ``max_value``, ``value`` y ``step`` → copiados tal cual del spec (``value``).
- ``key=f"input_{spec.name}"`` -> identificador del widget.



```python
def collect_values(st: Any) -> tuple[bool, dict[str, float]]:
    """TODO: renderiza ``FIELD_SPECS`` dentro de un único ``st.form``.

    Cada ``number_input`` debe recibir label, rango, default, step y una key
    estable. Devuelve ``(submitted, values)`` sin llamar al gateway.
    """
    with st.form("wine_quality_form"):
        values = {}
        for spec in FIELD_SPECS:
            values[spec.name] = st.number_input(
                label=spec.label,
                min_value=spec.min_value,
                max_value=spec.max_value,
                value=spec.default,
                step=spec.step,
                key=f"input_{spec.name}"
            )
        submitted = st.form_submit_button("Ejecutar inferencia")
    
    return (submitted, values)
```

### 03 Completa formulario y submit - Agrupa los widgets en un st.form y devuelve el estado de st.form_submit_button junto con values.
Agrupo los once widgets dentro de un ``st.form``. Ya está hecho en el 02.


### 04 Revisa la frontera gateway - Comprueba cero llamadas al editar y una al enviar, exclusivamente mediante gateway.predict(values).
La UI no conoce el modelo, solo habla con un ``InferenceGateway`` que expone ``predict(values) --> PredictionPayload``. ``PackagedBundleGateway`` es el adaptador que carga el bundle de S4 y traduce entre los dos contratos.

### 05 Presenta el resultado - Implementa render_prediction() con quality_band, confidence, model_version y preprocessing_version con copy honesto.
Muestro los cuatro campos de ``PredictionPayload``, cada uno con una etiqueta en español y el nombre del campo, para que se pueda trazar qué está viendo el usuario.

```python
def render_prediction(st: Any, prediction: PredictionPayload) -> None:
    """TODO: presenta los cuatro campos de ``PredictionPayload``."""
    
    st.write(f"Clase predicha (quality_band): {prediction.quality_band}.")
    st.write(f"Confianza (confidence): {prediction.confidence}.")
    st.write(f"Versión del modelo (model_version): {prediction.model_version}.")
    st.write(
        "Versión del preprocesado (preprocessing_version): "
        f"{prediction.preprocessing_version}."
    )
```

### 06 Prueba bundle ausente - Comprueba la frontera segura ante bundle ausente o inválido, sin rutas, traceback ni detalle interno.
Si el bundle no existe o está corrupto, ``load_model_bundle`` de S4 lanza excepciones con la ruta en el mensaje (``FileNotFoundError``), errores de ``joblib`` o errores de validación de pydantic. Nada de eso debe llegar al usuario.

```bash
export MODEL_UI_BUNDLE="assets/model/no_existe"
uv run streamlit run src/app.py
```
Output: No se pudo cargar el bundle de S4.



### 07 Ejecuta tests y QA - Deja 27 pruebas verdes y registra los cuatro casos con bundle real, edición, submit y bundle ausente.

```bash
uv run pytest 
```
Output: No se pudo cargar el bundle de S4.


### 08 Documenta ejecución y límites - Documenta el comando de arranque, la configuración del bundle y los límites que se abordarán en S6.

#### Ejecución

```bash
# Bundle real
export MODEL_UI_BUNDLE="assets/model/bundle"
uv run streamlit run src/app.py
```

```bash
# Bundle ausente
export MODEL_UI_BUNDLE="assets/model/no_existe"
uv run streamlit run src/app.py
```

#### Configuración del bundle
- ``MODEL_UI_BUNDLE``: ruta al directorio del bundle de S4. Debe contener ``manifest.json`` y ``model.joblib``.
- Por sencillez, añadí el bundle al directorio del ejercicios, en ``assets/models/bundle``.
- La ruta puede ser relativa a la carpeta desde la que se arranca la app, o absoluta.
- Si no está definida o el bundle no es válido, la UI muestra un mensaje genérico y no predice.

