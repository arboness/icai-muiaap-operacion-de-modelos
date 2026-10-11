"""TODO: transformación de una muestra validada en el vector del modelo."""

# Este contrato se entrega ya decidido: no cambies ni los nombres ni el orden.
# Implementa WineFeatures y preprocess_wine_request(). El orden anterior debe
# coincidir con el artefacto, no con un orden arbitrario del CSV.

MODEL_VERSION = "wine-quality-rf-error"

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

def preprocess_wine_request(wine_request):
   return [getattr(wine_request, name) for name in FEATURE_NAMES]