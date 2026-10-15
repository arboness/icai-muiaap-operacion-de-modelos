"""TODO: transformación de una muestra validada en el vector del modelo."""

# Este contrato se entrega ya decidido: no cambies ni los nombres ni el orden.
# Implementa WineFeatures y preprocess_wine_request(). El orden anterior debe
# coincidir con el artefacto, no con un orden arbitrario del CSV.
from dataclasses import dataclass

MODEL_VERSION = "wine-quality-rf-v1"

PREPROCESS_VERSION="wine-red-features-v1"

FEATURE_NAMES = [
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
    "alcohol",
]

@dataclass(frozen=True, slots=True)
class WineFeatures:
    fixed_acidity: float
    volatile_acidity: float
    citric_acid: float
    residual_sugar: float
    chlorides: float
    free_sulfur_dioxide: float
    total_sulfur_dioxide: float
    density: float
    ph: float
    sulphates: float
    alcohol: float

    def as_vector(self):
        return [getattr(self, name) for name in FEATURE_NAMES]


def preprocess_wine_request(request):
    data = request.model_dump()
    return WineFeatures(**{name: data[name] for name in FEATURE_NAMES})