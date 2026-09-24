1. **¿Qué campo identifica la muestra?**
    - El campo ``sample_id`` identifica la muestra.

2. **¿Qué once campos consume el modelo?**
    - ``sample_id`` 
    - ``fixed_acidity`` 
    ``volatile_acidity``
    - ``citric_acid``
    - ``residual_sugar``
    - ``chlorides``
    - ``free_sulfur_dioxide``
    - ``total_sulfur_dioxide``
    - ``densit``
    - ``ph``
    - ``sulphates``
    - ``alcohol``

3. **Proponed una nueva columna que el contrato debería rechazar**
    - El contrato no va a rechazar la creación de una nueva columna ya que no existe una regla que limite el número de columnas.

4. **Proponed valores inválidos y explicad por qué:**
    - ``sample_id``: Un entero como ``340`` o vacío, ya que la longitud mínima es 1.
    - ``fixed_acidity``: ``"yes"`` ya que hay una regla que dice que es un float. Tamibén serviría ``-1``, ya que el valor debe ser mayor o igual a 0. . 

