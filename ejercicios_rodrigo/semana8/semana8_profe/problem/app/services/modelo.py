import joblib

from app.config import MODEL_PATH
from app.schemas.prestamo import PrediccionSalida, PrestamoEntrada

# Orden en el que el modelo espera las variables
VARIABLES = [
    "edad",
    "ingresos_mensuales",
    "importe_prestamo",
    "plazo_meses",
    "antiguedad_laboral_anios",
    "impagos_previos",
]

# TODO: cargar el modelo joblib una sola vez, al importar el modulo
model = joblib.load(MODEL_PATH)
# TODO: funcion decidir(probabilidad) -> "aprobar", "revisar" o "rechazar" (umbrales en el enunciado)
def decidir(probabilidad)->str:
    if probabilidad <= 0.2:
        return 'aprobar'
    if probabilidad <=0.5:
        return 'revisar'
    
    return 'rechazar'

# TODO: funcion predecir(entrada) -> PrediccionSalida, usando VARIABLES para ordenar los valores
def predecir(entrada: PrestamoEntrada)->PrediccionSalida:
    entrada_ordenada = []
    for var in VARIABLES:
        entrada_ordenada.append(getattr(entrada, var))
    
    prob = model.predict_proba([entrada_ordenada])[0][1]
    decision = decidir(prob)
    
    return PrediccionSalida(probabilidad_impago=prob, decision=decision)

