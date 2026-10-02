## Entregable

Incluye en la ficha de semana 01 el identificador de una traza, el resultado de la evaluación y una limitación concreta de este scorer. ¿Aprueba una respuesta sólo por contener una frase? ¿Qué controles adicionales harían falta?

- __Identificador de una traza:__ tr-4ffe4b9ac75ee3d260ed9e9dfa6b444e
- __Resultado de la evaluación: __
    -  `contains_expected_phrase/mean`: 0.625.
    - `response_is_concise/mean`: 1.0.
    - `safety_refusal/mean`: 0.75.
- __Limitación del scorer?:__ Para el `response_is_concise`,  
- __Aprueba respuesta por contener una frase?__: Sí, siempre que tenga menos de 60 palabras, sea una respuesta dentro de las "esperadas" y sea "segura" sí.
- __Controles adicionales__: En el caso de LLM, comprobar más palabras y hacer expresiones regulares para evitar palabras como t0ken en vez de token. Comprobar  