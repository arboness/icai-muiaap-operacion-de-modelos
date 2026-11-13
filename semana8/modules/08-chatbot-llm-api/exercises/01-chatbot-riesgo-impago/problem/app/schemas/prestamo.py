from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class PrestamoEntrada(BaseModel):
    """Datos de una solicitud de prestamo. Es el unico contrato: lo usan /predict y la tool del LLM."""

    # extra="forbid": si el LLM (o un cliente) se inventa un campo, se rechaza
    model_config = ConfigDict(extra="forbid")

    edad: int = Field(ge=18, le=75, description="Edad del solicitante en anios")
    ingresos_mensuales: float = Field(gt=0, description="Ingresos netos mensuales en euros")
    importe_prestamo: float = Field(gt=0, description="Importe solicitado en euros")
    plazo_meses: int = Field(ge=6, le=84, description="Plazo de devolucion en meses")
    antiguedad_laboral_anios: int = Field(
        ge=0, le=50, description="Anios de antiguedad laboral (no mayor que edad - 16)"
    )
    impagos_previos: int = Field(ge=0, le=20, description="Numero de impagos previos")

    @field_validator("antiguedad_laboral_anios")
    @classmethod
    def antiguedad_coherente_con_edad(cls, valor, info):
        edad = info.data.get("edad")
        # Si la edad ya fallo su propia validacion no esta en info.data: no duplicamos el error
        if edad is not None and valor > edad - 16:
            raise ValueError(
                f"la antiguedad laboral ({valor}) no puede ser mayor que edad - 16 ({edad - 16})"
            )
        return valor


class PrediccionSalida(BaseModel):
    probabilidad_impago: float = Field(ge=0, le=1)
    decision: Literal["aprobar", "revisar", "rechazar"]
