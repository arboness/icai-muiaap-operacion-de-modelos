# Problema — Diseñar el contrato del bundle

Trabajad en parejas con el notebook
01-artefacto-y-manifiesto-alumno.ipynb. Partís del payload legado de la semana
3, que contiene estimator, feature_names y model_version.

## Entrega

Completad en el notebook:

- una tabla que asigne cada dato a model.joblib, manifest.json o código;
- el manifiesto propuesto con las seis claves obligatorias;
- tres invariantes que el cargador debe comprobar;
- dos entradas inválidas y la etapa en la que deben fallar;
- una decisión sobre qué hacer si la segunda fila del CSV es inválida.

No implementéis todavía artifact.py. La clase 2 empieza con ese diseño y lo
convierte en funciones y pruebas.
