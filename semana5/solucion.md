# Readme de explicación de las soluciones de la semana 5
## Ejercicio 1
### Lee el contrato y anticipa dos predicciones · 0–10 min - Lee la firma de predict() y anticipa el resultado para los perfiles 2, 95, 4, False y 36, 35, 0, True.
```python
risk_score = round(min(0.95, max(0.05, score)), 2)
```
 - **(2, 95, 4, False)**: 0.3 + 0.8  + 0.25 + 0.1 = 1.45 -> 0.95. Lo máximo para valores >0.95 es 0.95.
- **(36, 35, 0, True)**: -0.15 - 0.05 + 0 - 0.25 = -0.45 -> 0.05, lo mínimo es un 5% de probabilidad.
### Construye el formulario · 10–25 min - Crea los cuatro widgets dentro de un único st.form y añade st.form_submit_button
Se crea el formulario con las ``keys`` esperadas por los tests y con la información y valores requeridos.
```python
def collect_profile(st: Any) -> tuple[bool, dict[str, object]]:

    with st.form("churn_form"):
        tenure_months = st.slider("Antigüedad", 0, 120, 12, key="tenure_months")
        monthly_spend_eur = st.number_input("Gasto mensual",min_value = 0.0, max_value=300.0, value=60.0, step = 0.5, format = "%.2f",key="monthly_spend_eur" )
        support_calls = st.slider("Llamadas a sporte", min_value = 0, max_value=20, value=1, key="support_calls")
        has_annual_contract = st.checkbox("Contrato anual", value = False, key="has_annual_contract")
        
        
        
        submitted = st.form_submit_button("Calcular riesgo")

    profile = {
        "tenure_months": tenure_months,
        "monthly_spend_eur": monthly_spend_eur,
        "support_calls": support_calls,
        "has_annual_contract": has_annual_contract,
    }
    return submitted, profile
```


### 03 Conecta submit y predict() · 25–35 min - Mientras se edita debe haber cero llamadas; cada envío válido hace una llamada a predict()
Se llama a la función ``predict`` (aka ``predictor``), se guarda el resultado y se muestra con ``render_prediction``. Si se produce un ``ValueError``, se captura y se muestra la usuario.

```python
def run_app(st: Any, predictor: Predictor) -> None:
    """Conecta submit, llamada al predictor y actualización visible."""
    submitted, profile = collect_profile(st)

    if submitted:
        try:
            result = predictor(**profile)
            render_prediction(st, result)
        except ValueError as e:
            st.error(f"No se pudo calcular la predicción.")
```

### 04 Presenta resultado y error · 35–45 min - Muestra label, risk_score y explanation con etiquetas claras y traduce ValueError a un mensaje seguro
Se muestra lo que devuelve el modelo. Si se ha producido un ``ValueError``, ya se ha capturado y mostrado en la función ``run_app``, que llama a ``render_prediction``.

```python

def render_prediction(st: Any, result: ChurnPrediction) -> None:
    st.write("Resultado de la predicción")

    st.metric("Clasificación", str(result["label"]))
    st.metric("Score de riesgo (orientativo)", f"{result['risk_score']:.2f}")

    if result["will_churn"]:
        st.warning(result["label"])
    else:
        st.success(result["label"])

    if result.get("explanation"):
        st.info("**¿Por qué?**")
        st.write(result["explanation"])
```

### 05 Ejecuta los tests · 45–55 min - Corrige cada contrato incumplido hasta dejar las 13 pruebas verdes y el formato limpio
TUve que cambiar algunas cosas ya que los tests esperaban otros mensajes de error y otros elementos de streamlit. Como se usa una "simulación" de streamlit, no he podido utilizar elementos de streamlit como ``header``, ``subheader`` o ``markdown`` ya que ``FakeStreamlit`` no los tiene definidos.

### 06 Cierra QA y puente · 55–60 min - Registra los cuatro casos manuales y explica qué patrón se conservará al pasar al contrato Wine.
- ¿Qué cuatro casos manuales? No entiendo esto. Ya he probado diferentes casos y ya he pasado todos los tests.

- Al pasar al caso de calidad del vino solo cambian el contrato de datos y la presentación:

    - **Inferencia separada de la UI:** una función `predict(**features)` que no sabe nada de Streamlit y devuelve un resultado estructurado (etiqueta, score, explicación).
  
    - **Formulario con envío explícito:** `st.form` + `st.form_submit_button`, con una clave por widget, para no lanzar inferencias en cada edición. Los widgets pasan a ser las variables del vino (acidez, azúcar residual, alcohol, etc.).
  
    - **`collect_profile` -> `run_app` -> `render_prediction`:** recoger valores, llamar al predictor una sola vez tras el submit y presentar el resultado sin recalcular nada.
    
    - **Predictor inyectable:** `run_app(st, predictor)` permite probar con un predictor falso y un `FakeStreamlit` sin abrir el navegador.
    
    - **Errores seguros:** un `ValueError` se convierte en un mensaje legible sin exponer detalles internos.
    
    - **Tests del contrato:** 0 llamadas sin submit, 1 llamada con los valores de los widgets, presentación de etiqueta/score/explicación y error humano.


## Ejercicio 2