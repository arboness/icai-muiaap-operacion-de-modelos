from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

TipoDecision = Literal['aprobar', 'revisar', 'rechazar']

# TODO: clase PrestamoEntrada (BaseModel) con las 6 variables del modelo, con sus rangos (ver enunciado).
#       Debe rechazar campos que no existan.

class PrestamoEntrada(BaseModel):
    model_config = ConfigDict(extra="forbid")
    
    edad: int = Field(ge=18, le=75, description="La edad debe ser mayor o igual a 18 y menor o igual a 75.")
    ingresos_mensuales: float = Field(gt=0, description="Ingresos")
    importe_prestamo: float = Field(gt=0)
    plazo_meses: int = Field(ge=6, le=84)
    antiguedad_laboral_anios: int = Field(ge=0, le=50)
    impagos_previos: int = Field(ge=0, le=20)
    # TODO: field_validator (con classmethod) para antiguedad_laboral_anios: no puede ser incoherente con la edad.
    @model_validator(mode="after")
    def validate_antiguedad_laboral(self):
        if not self.antiguedad_laboral_anios <= self.edad - 16:
            raise ValueError("Error: La antiguedad laboral no debe ser menor a la edad - 16 anios.")
        return self

    

# TODO: clase PrediccionSalida con probabilidad_impago (entre 0 y 1) y decision (aprobar, revisar o rechazar).
class PrediccionSalida(BaseModel):
    model_config = ConfigDict(extra="forbid")

    probabilidad_impago: float = Field(ge=0, le=1)
    decision: TipoDecision = Field()