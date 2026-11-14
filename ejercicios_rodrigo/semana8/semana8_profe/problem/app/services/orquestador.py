import json

from pydantic import ValidationError

from app.schemas.chat import ChatSalida, HerramientaUsada, Mensaje
from app.schemas.prestamo import PrestamoEntrada
from app.services.modelo import predecir

NOMBRE_TOOL = "calcular_riesgo_impago"
MAX_VUELTAS = 4

SISTEMA = (
    "Eres un asistente de riesgo de un banco. Cuando tengas todos los datos de una solicitud de "
    "prestamo, llama a la herramienta calcular_riesgo_impago. Si falta algun dato, pidelo. "
    "Nunca inventes valores. Responde en espanol y de forma breve."
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


# TODO: definir_tool() -> dict con la definicion de la tool, sacando "parameters" de PrestamoEntrada

def definir_tool():
    esquema = PrestamoEntrada.model_json_schema()
 
    return {
        "type": "function",
        "function": {
            "name": NOMBRE_TOOL,  
            "description": "Calcula la probabilidad de impago de una solicitud de préstamo usando el modelo del banco. "
                           "Úsala solo cuando tengas los seis datos del cliente.",
            "parameters": esquema,
        },
    }
    
# TODO: ejecutar_tool(nombre, argumentos_json) -> dict con "ok" True/False
#       (tool desconocida, JSON roto, datos invalidos o campos inventados -> ok False con el error)

def ejecutar_tool(nombre, argumentos_json):
    if nombre != NOMBRE_TOOL:
        return {"ok": False, 'error': "Nombre de tool inesperado"}
    argumentos_dict = leer_argumentos(argumentos_json)
    try:
        entrada = PrestamoEntrada(**argumentos_dict)
        respuesta = predecir(entrada)
    except ValidationError as e:
        return {"ok": False, 'error': str(e)}
    return {'ok': True, **respuesta.model_dump()}

def responder(mensajes, llm):
    historial = [{"role": "system", "content": SISTEMA}]
    historial += [m.model_dump() for m in mensajes]
    herramienta = None

    for _ in range(MAX_VUELTAS):
        mensaje = llm.completar(historial, [definir_tool()])

        if not mensaje.get("tool_calls"):
            return ChatSalida(respuesta=mensaje.get("content") or "", herramienta=herramienta)

        historial.append({
            "role": "assistant",
            "content": mensaje.get("content"),
            "tool_calls": mensaje["tool_calls"],
        })

        for llamada in mensaje["tool_calls"]:
            nombre = llamada["function"]["name"]
            argumentos = llamada["function"]["arguments"]

            resultado = ejecutar_tool(nombre, argumentos)
            herramienta = HerramientaUsada(
                nombre=nombre,
                argumentos=leer_argumentos(argumentos),
                resultado=resultado,
            )
            historial.append({
                "role": "tool",
                "tool_call_id": llamada["id"],
                "content": json.dumps(resultado),
            })

    return ChatSalida(
        respuesta="No he podido completar el cálculo con los datos recibidos. ¿Puedes revisarlos?",
        herramienta=herramienta,
    )
# TODO: responder(mensajes, llm) -> ChatSalida, con el bucle LLM -> tool -> LLM (maximo MAX_VUELTAS)
