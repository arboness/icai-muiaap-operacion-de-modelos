import json

from pydantic import ValidationError

from app.schemas.chat import ChatSalida, HerramientaUsada
from app.schemas.prestamo import PrestamoEntrada
from app.services.modelo import predecir

NOMBRE_TOOL = "calcular_riesgo_impago"
MAX_VUELTAS = 4

SISTEMA = (
    "Eres un asistente de riesgo de un banco. Cuando tengas todos los datos de una solicitud de "
    "prestamo, llama a la herramienta calcular_riesgo_impago. Si falta algun dato, pidelo. "
    "Nunca inventes valores. Responde en espanol y de forma breve."
)

RESPUESTA_SIN_CONCLUIR = (
    "No he podido completar el calculo con los datos recibidos. "
    "Revisa los datos de la solicitud y vuelve a intentarlo."
)


def leer_argumentos(texto):
    """YA HECHO: convierte el texto JSON de la tool en dict ({} si no es JSON valido)."""
    try:
        datos = json.loads(texto)
    except (json.JSONDecodeError, TypeError):
        return {}
    if isinstance(datos, dict):
        return datos
    return {}


def definir_tool():
    """Definicion de la tool para el LLM. Los parametros salen de PrestamoEntrada (un unico contrato)."""
    return {
        "type": "function",
        "function": {
            "name": NOMBRE_TOOL,
            "description": (
                "Calcula la probabilidad de impago de una solicitud de prestamo con el modelo "
                "del banco y devuelve la decision (aprobar, revisar o rechazar)."
            ),
            "parameters": PrestamoEntrada.model_json_schema(),
        },
    }


def _describir_errores(error):
    """Convierte un ValidationError en un texto corto que el LLM pueda entender."""
    partes = []
    for detalle in error.errors():
        campo = ".".join(str(trozo) for trozo in detalle["loc"]) or "entrada"
        partes.append(f"{campo}: {detalle['msg']}")
    return "Datos invalidos -> " + "; ".join(partes)


def ejecutar_tool(nombre, argumentos_json):
    """Ejecuta la tool pedida por el LLM. Nunca lanza excepcion: devuelve siempre un dict con "ok"."""
    if nombre != NOMBRE_TOOL:
        return {"ok": False, "error": f"Herramienta desconocida: {nombre}"}

    try:
        argumentos = json.loads(argumentos_json)
    except (json.JSONDecodeError, TypeError):
        return {"ok": False, "error": "Los argumentos no son un JSON valido"}
    if not isinstance(argumentos, dict):
        return {"ok": False, "error": "Los argumentos deben ser un objeto JSON"}

    try:
        entrada = PrestamoEntrada(**argumentos)
    except ValidationError as error:
        return {"ok": False, "error": _describir_errores(error)}

    try:
        salida = predecir(entrada)
    except Exception as error:  # el LLM nunca debe ver una excepcion, solo un resultado
        return {"ok": False, "error": f"Error al ejecutar el modelo: {error}"}

    return {"ok": True, **salida.model_dump()}


def responder(mensajes, llm):
    """Bucle LLM -> tool -> LLM hasta que el LLM conteste con texto (como mucho MAX_VUELTAS)."""
    historial = [{"role": "system", "content": SISTEMA}]
    for mensaje in mensajes:
        historial.append({"role": mensaje.role, "content": mensaje.content})

    herramientas = [definir_tool()]
    herramienta_usada = None

    for _ in range(MAX_VUELTAS):
        respuesta = llm.completar(historial, herramientas)
        llamadas = respuesta.get("tool_calls") or []

        if not llamadas:
            return ChatSalida(respuesta=respuesta.get("content") or "", herramienta=herramienta_usada)

        historial.append(
            {"role": "assistant", "content": respuesta.get("content"), "tool_calls": llamadas}
        )
        for llamada in llamadas:
            nombre = llamada["function"]["name"]
            argumentos_json = llamada["function"]["arguments"]
            resultado = ejecutar_tool(nombre, argumentos_json)
            herramienta_usada = HerramientaUsada(
                nombre=nombre, argumentos=leer_argumentos(argumentos_json), resultado=resultado
            )
            historial.append(
                {
                    "role": "tool",
                    "tool_call_id": llamada.get("id"),
                    "content": json.dumps(resultado),
                }
            )

    return ChatSalida(respuesta=RESPUESTA_SIN_CONCLUIR, herramienta=herramienta_usada)
