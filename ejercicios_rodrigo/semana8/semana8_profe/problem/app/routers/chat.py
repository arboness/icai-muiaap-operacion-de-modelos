from fastapi import APIRouter, Depends

from app.schemas.chat import ChatEntrada, ChatSalida
from app.services.llm import get_llm
from app.services.orquestador import responder

router = APIRouter()

#get_llm se pasa sin paréntesis, esto es porque yo le digo a FASTAPI el objeto de la función que necesita ejecutar, y el framework la ejecuta.
@router.post('/chat', response_model=ChatSalida)
def chat(entrada: ChatEntrada, llm=Depends(get_llm)) -> ChatSalida:
    return responder(entrada.mensajes, llm)
# TODO: POST /chat (entrada ChatEntrada, salida ChatSalida). Recibe el LLM con Depends(get_llm)
