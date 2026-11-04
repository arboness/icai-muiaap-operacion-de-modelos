# Readme de explicación de las soluciones de la semana 5
### 01 
```python
st.set_page_config(page_title="S5 · Primera app")
st.title("Mi primera interfaz")
st.caption("Churn sintético · ejemplo docente")
st.write("Python dibuja la pantalla. El navegador permite interactuar.")
```
### 02 
Se introducen los datos con ``number_input`` y se almacenan en variables.


```python
from datetime import datetime
import streamlit as st

st.title("Entradas y rerun")
st.caption("Última ejecución: " + datetime.now().isoformat(timespec="microseconds"))
tenure = st.number_input("Antigüedad (meses)", min_value=0, max_value=120, value=2, step=1)
spend = st.number_input("Gasto mensual (EUR)", min_value=0.0, max_value=300.0, value=95.0, step=1.0)
calls = st.number_input("Llamadas a soporte", min_value=0, max_value=20, value=4, step=1)
annual = st.checkbox("Contrato anual", value=False)
st.write({"tenure_months": tenure, "monthly_spend_eur": spend,
          "support_calls": calls, "has_annual_contract": annual})
st.info("Aquí solo recogemos valores. No ejecutamos inferencia.")

```

### 03 
Esta vez en forma de formulario. Si se pulsa el botón ``Enviar perfil``, se muestran los dato sintroducidos. Si no, se muestra un mensaje informativo.

```python
from datetime import datetime
import streamlit as st

st.title("Editar no es enviar")
st.caption("Última ejecución: " + datetime.now().isoformat(timespec="microseconds"))
with st.form("churn_form"):
    tenure = st.number_input("Antigüedad (meses)", min_value=0, max_value=120, value=2, step=1)
    spend = st.number_input("Gasto mensual (EUR)", min_value=0.0, max_value=300.0, value=95.0, step=1.0)
    calls = st.number_input("Llamadas a soporte", min_value=0, max_value=20, value=4, step=1)
    annual = st.checkbox("Contrato anual", value=False)
    submitted = st.form_submit_button("Enviar perfil")

if submitted:
    st.write({"tenure_months": tenure, "monthly_spend_eur": spend,
              "support_calls": calls, "has_annual_contract": annual})
else:
    st.info("Completa el formulario y envíalo.")

```


### 04 
Se añade sobre la 02 y la 03 la inferencia. Se recogen los datos con un formulario. Se realiza la inferencia y se muestra al usuario.
```python
import streamlit as st
from model import predict

st.set_page_config(page_title="S5 · Churn sintético")
st.title("¿Qué cliente podría darse de baja?")
st.caption("Regla docente sintética; no es una probabilidad calibrada.")
simulate_error = st.checkbox("Demo docente: provocar un error de contrato", value=False)
with st.form("churn_form"):
    tenure = st.number_input("Antigüedad (meses)", min_value=0, max_value=120, value=2, step=1)
    spend = st.number_input("Gasto mensual (EUR)", min_value=0.0, max_value=300.0, value=95.0, step=1.0)
    calls = st.number_input("Llamadas a soporte", min_value=0, max_value=20, value=4, step=1)
    annual = st.checkbox("Contrato anual", value=False)
    submitted = st.form_submit_button("Calcular riesgo")

if submitted:
    values = {"tenure_months": tenure, "monthly_spend_eur": spend,
              "support_calls": calls, "has_annual_contract": annual}
    if simulate_error:
        values["tenure_months"] = -1
    try:
        result = predict(**values)
    except ValueError:
        st.error("No se pudo calcular el riesgo. Revisa los datos e inténtalo de nuevo.")
    else:
        st.subheader(result["label"])
        st.metric("Score orientativo (0 a 1)", f"{result['risk_score']:.2f}")
        st.write(result["explanation"])
else:
    st.info("Completa el formulario y pulsa Calcular riesgo.")

```
