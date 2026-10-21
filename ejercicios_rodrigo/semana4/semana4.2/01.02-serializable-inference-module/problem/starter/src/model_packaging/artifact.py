"""Puntos de extensión del taller de serialización."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any, Protocol
import joblib
from pydantic import BaseModel, ConfigDict, Field, field_validator

from model_packaging.contracts import (
    QualityBand,
    WineQualityPrediction,
    WineQualityRequest,
)

from model_packaging.preprocess import PREPROCESSING_VERSION, FEATURE_NAMES, preprocess_wine_request

SCHEMA_VERSION = "v1.0"
MODEL_VERSION = "wine-quality-rf-v1"
DEFAULT_BUNDLE_PATH = Path("models/wine_quality_bundle")
MANIFEST_FILENAME = "manifest.json"
MODEL_FILENAME = "model.joblib"
ESTIMATOR_TYPE = "RandomForestClassifier" 
OUTPUT_LABELS: tuple[QualityBand, ...] = (
    "acceptable",
    "excellent",
    "needs_review",

)


class WineQualityEstimator(Protocol):
    """Interfaz mínima que debe cumplir el estimador cargado."""

    def predict(self, features: list[list[float]]) -> Sequence[str]:
        """Devuelve una etiqueta por fila."""

    def predict_proba(self, features: list[list[float]]) -> Sequence[Sequence[float]]:
        """Devuelve probabilidades por fila."""


class ArtifactManifest(BaseModel):
    """TODO: declara y valida los metadatos del bundle."""

    model_config = ConfigDict(extra="forbid")

    schema_version: str = Field(min_length=1)
    model_version: str = Field(min_length=1)
    preprocessing_version: str = Field(min_length=1)
    feature_names: tuple[str, ...] = Field(min_length=1)
    output_labels: tuple[QualityBand, ...] = Field(min_length=1)
    estimator_type: str = Field(min_length=1)

    
    @field_validator("schema_version")
    @classmethod
    def validate_schemaversion(cls, value):
        if value != SCHEMA_VERSION:
            raise ValueError(f"La versión del esquema recibida {value} no es la esperada. Se esperaba {SCHEMA_VERSION}")

        return value
    
    @field_validator("preprocessing_version")
    @classmethod
    def validate_preprocessing_version(cls, value):
        if value != PREPROCESSING_VERSION:
            raise ValueError(f"La versión del preprocesado recibida {value} no es la esperada. Se esperaba {PREPROCESSING_VERSION}")

        return value
    
    @field_validator("feature_names")
    @classmethod
    def validate_feature_names(cls, value):
        if value != FEATURE_NAMES:
            raise ValueError(f"Las features recibidas {value} no son las esperadas. Se esperaba {FEATURE_NAMES}")

        return value
    
    @field_validator("output_labels")
    @classmethod
    def validate_output_labels(cls, value):
        if value != OUTPUT_LABELS:
            raise ValueError(f"Las etiquetas de salida recibidas {value} no son las esperadas. Se esperaba {OUTPUT_LABELS}")

        return value
    
    
@dataclass(frozen=True)
class LoadedModelBundle:
    """Bundle cargado; no modificar esta interfaz pública."""

    estimator: WineQualityEstimator
    manifest: ArtifactManifest


def create_manifest(
    estimator: WineQualityEstimator, model_version: str
) -> ArtifactManifest:
    """devuelve un manifiesto compatible con el contrato."""
    return ArtifactManifest(
        schema_version=SCHEMA_VERSION,
        model_version=model_version,
        preprocessing_version=PREPROCESSING_VERSION,
        feature_names=FEATURE_NAMES,
        output_labels=OUTPUT_LABELS,
        estimator_type=type(estimator).__name__,
        
    )


def save_model_bundle(
    bundle_path: Path,
    estimator: WineQualityEstimator,
    manifest: ArtifactManifest | None = None,
) -> ArtifactManifest:
    """TODO: escribe manifest.json y model.joblib de forma segura."""

    if manifest is None:
        manifest = create_manifest(estimator, MODEL_VERSION)

    bundle_path.mkdir(parents=True, exist_ok=True)

    with open(bundle_path / MANIFEST_FILENAME, "w", encoding="utf-8") as f:
        json.dump(manifest.model_dump(mode="json"), f, indent=4, ensure_ascii=False)

    joblib.dump(estimator, bundle_path / MODEL_FILENAME)

    return manifest
  


def load_model_bundle(bundle_path: Path) -> LoadedModelBundle | None:
    """TODO: valida el manifiesto antes de cargar el estimador."""
    
    manifest_path = bundle_path / MANIFEST_FILENAME
    estimator_path = bundle_path / MODEL_FILENAME
    
    if not manifest_path.exists():
        raise FileNotFoundError(f"El archivo {manifest_path} no existe.")
    
    if not estimator_path.exists():
        raise FileNotFoundError(f"El archivo {estimator_path} no existe.")
    
    with open(manifest_path, 'r') as f:
        manifest = json.load(f)
    
    validated_manifest = ArtifactManifest.model_validate(manifest)
        
    estimator = joblib.load(estimator_path)
    
    return LoadedModelBundle(estimator=estimator, manifest=validated_manifest)


def infer_wine_quality(
    bundle: LoadedModelBundle,
    request: WineQualityRequest,
) -> WineQualityPrediction:
    """TODO: preprocesa, invoca el estimador y valida la respuesta."""

    features = preprocess_wine_request(request).as_vector()

    label = bundle.estimator.predict([features])[0]
    probabilities = bundle.estimator.predict_proba([features])[0]

    return WineQualityPrediction(
        quality_band=str(label),
        confidence=float(max(probabilities)),
        model_version=bundle.manifest.model_version,
        preprocessing_version=bundle.manifest.preprocessing_version,
    )