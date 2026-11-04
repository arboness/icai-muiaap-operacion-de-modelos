# Readme de explicación de las soluciones de la semana 6

### 01 Contador roto

No tiene memoria, cada vez que se pulsa el botón se vuelve a ejecutar streamlit perdiendo el contexto anterior.

```python
st.title("Contador sin memoria")
count = 0
if st.button("Sumar"):
    count += 1
st.metric("Cuenta", count)
```

### 02 Contador estado

Se introduce el ``session_state``. Diccionario que se inicializa cada vez que se lanza streamlit. En cuanto se lanza el script, se añade contador al ``session_state``. Si se acciona el botón, se incrementa el valor del diccionario asociado al contador.

```python
import streamlit as st
st.title("Contador con estado")
if "count" not in st.session_state:
    st.session_state.count = 0
if st.button("Sumar"):
    st.session_state.count += 1
st.metric("Cuenta", st.session_state.count)
```

### 03 Contador callback
En vez de añadirlo directamente, defino una función y la llamo cada vez que se ejecute la acción de pulsar.
```python
import streamlit as st
st.title("Contador con callback")
if "count" not in st.session_state:
    st.session_state.count = 0
def increment():
    st.session_state.count += 1
    
st.button("Sumar", on_click=increment)
st.metric("Cuenta", st.session_state.count)

```

### 04 App ejemplo
Es la app de ejemplo proporcionada.

### 05 Práctica starter
Jugamos con los callbacks y con el ``session_state``. Permitimos realizar predicciones al usuario y las almacenamos en la clave ``history`` de ``session_state``. Las mostramos como dataframe.
```python

import streamlit as st
from modelo import predict_toy

st.set_page_config(page_title="Churn con memoria", layout="centered")
st.title("Churn con memoria")
st.caption("Regla de juguete. No usar para tomar decisiones sobre clientes.")

# A: iniciar una sola vez, no en cada rerun.
if "history" not in st.session_state:
    st.session_state.history = []

def submit_prediction():
    # Leer los valores nuevos desde las keys, no mediante args del callback.
    inputs = {name: st.session_state[name] for name in
              ("tenure_months", "monthly_spend_eur", "contract", "support_calls")}
    result = predict_toy(**inputs)
    # B: una fila por submit. No predecir en cada rerun.
    # TODO B: añadir {**inputs, **result} a history
    st.session_state.history.append({**inputs, **result})

def clear_history():
    st.session_state.history = []

with st.form("churn_form"):
    st.slider("Antigüedad (meses)", 0, 72, 6, key="tenure_months")
    st.number_input("Gasto mensual (EUR)", 0.0, 200.0, 80.0,
                    step=5.0, key="monthly_spend_eur")
    st.selectbox("Contrato", ["Mensual", "Anual"], key="contract")
    st.slider("Llamadas a soporte", 0, 5, 2, key="support_calls")
    st.form_submit_button("Predecir y guardar", on_click=submit_prediction)

# Fuera del form: provoca rerun sin añadir otra predicción.
st.checkbox("Mostrar ayuda", key="show_help")
if st.session_state.show_help:
    st.info("El form envía todos sus valores al pulsar submit. El historial vive en esta sesión.")

# C: mostrar un contador y, si hay filas, st.dataframe.
# Pista: history = st.session_state.get("history", [])
st.info("TODO C: dibuja aquí el historial y su contador.")

history = st.session_state.get("history", [])
st.metric("Filas", len(history)/2)
if len(history) != 0:
    st.dataframe(history)

st.button("Vaciar historial", on_click=clear_history)
st.caption("Recargar el navegador o cerrar la conexión puede borrar la sesión. No es una base de datos.")

```