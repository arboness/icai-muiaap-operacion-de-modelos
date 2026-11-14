from fastapi import APIRouter

from app.schemas.prestamo import PrediccionSalida, PrestamoEntrada
from app.services.modelo import predecir

router = APIRouter(
    prefix='/predict'
)

@router.post("/", response_model=PrediccionSalida)
def predict(entrada: PrestamoEntrada)->PrediccionSalida:
    return predecir(entrada)
# TODO: POST /predict (entrada PrestamoEntrada, salida PrediccionSalida)
