## Explicación

- Con pydantic, se ha realizado un contrato de entrada de datos para que, antes d eprobar un modelo, comprobar que los datos que se pasan siguen la estructura que el modelo espera. Como no sé qué rangos son los correctos, he puesto algunos valores por decisión propia pero que acepten los datos del csv. 

- El contrato se encuentra en el archivo ``src/semana3/contract.py``. 

- Para probarlo, se debe de ejecutar el archivo ``src/semana3/contract_test.py`` con ``uv run python -m semana3.contract_test``.

## Conclusión

Un contrato de datos es necesario ya que, si queremos que nuestro modelo le funcione a más personas, los datos que introducen esas personas deben de coincidir con los datos con los que fue entrenado el modelo. **No se puede entrenar un modelo con peras y después probarlo con manzanas.**

