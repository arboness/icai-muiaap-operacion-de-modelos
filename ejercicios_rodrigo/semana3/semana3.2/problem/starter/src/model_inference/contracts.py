from pydantic import BaseModel, ConfigDict, Field
from typing import Literal

# Implementa WineQualityRequest y WineQualityPrediction con Pydantic.
# Revisa los campos de assets/inference_samples.csv y prohíbe columnas extra.

WineQualityLabel = Literal["acceptable", "needs_review"]



class WineQualityRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    
    sample_id: str = Field(min_length=1) 
    fixed_acidity: float = Field(ge=0,le=20, description="Fixed acidity of the wine sample")
    volatile_acidity: float = Field(ge=0, le=2, description="Volatile acidity of the wine sample")
    citric_acid: float = Field(ge=0, le=2, description="Citric acid of the wine sample")
    residual_sugar: float = Field(ge=0,le=20, description="Residual sugar of the wine sample")
    chlorides: float = Field(ge=0, le=1, description="Chlorides of the wine sample")
    free_sulfur_dioxide: float = Field(ge=0, le=100, description="Free sulfur dioxide of the wine sample")
    total_sulfur_dioxide: float = Field(ge=0, le=300, description="Total sulfur dioxide of the wine sample")
    density: float = Field(ge=0.98, le=1.01, description="Density of the wine sample")
    ph: float = Field(ge=2.5, le=4.5, description="pH of the wine sample")
    sulphates: float = Field(ge=0, le=3, description="Sulphates of the wine sample")
    alcohol: float = Field(ge=5, le=20, description="Alcohol content of the wine sample")
    
class WineQualityPrediction(BaseModel):
    model_config = ConfigDict(extra="forbid")

    wine_quality: WineQualityLabel = Field(description="Predicted quality class of a wine sample")