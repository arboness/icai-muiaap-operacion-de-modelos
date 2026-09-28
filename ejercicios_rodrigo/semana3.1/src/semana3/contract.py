from pydantic import BaseModel, ConfigDict, Field


class WineInputSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")
    
    sample_id: str = Field(..., min_length=1, description="Unique identifier for the wine sample")
    fixed_acidity: float = Field(...,ge=0, le=20, description="Fixed acidity of the wine sample")
    volatile_acidity: float = Field(...,ge=0, le=2, description="Volatile acidity of the wine sample")
    citric_acid: float = Field(...,ge=0, le=10, description="Citric acid of the wine sample")
    residual_sugar: float = Field(...,ge=0, le=10, description="Residual sugar of the wine sample")
    chlorides: float = Field(...,ge=0, le=10, description="Chlorides of the wine sample")
    free_sulfur_dioxide: float = Field(..., ge=0, le=100, description="Free sulfur dioxide of the wine sample")
    total_sulfur_dioxide: float = Field(..., ge=0, le=100, description="Total sulfur dioxide of the wine sample")
    density: float = Field(..., ge=0, le=10, description="Density of the wine sample")
    ph: float = Field(..., ge=0, le=10, description="pH of the wine sample")
    sulphates: float = Field(..., ge=0, le=10, description="Sulphates of the wine sample")
    alcohol: float = Field(..., ge=0, le=10, description="Alcohol content of the wine sample")