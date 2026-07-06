from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from app.services.ai_engine import ai_engine

router = APIRouter()

class ChatRequest(BaseModel):
    # El frontend nos enviará la lista con el historial completo de la conversación
    messages: list

@router.post("/chat")
async def chat_endpoint(request: ChatRequest):
    try:
        # Retornamos una respuesta en streaming (letra por letra)
        return StreamingResponse(
            ai_engine.generar_respuesta_stream(request.messages),
            media_type="text/event-stream"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))