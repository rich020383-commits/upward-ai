import os
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

# 1. Inicializamos el nuevo cliente oficial moderno
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

router = APIRouter(
    prefix="/api/chat",
    tags=["Asistente IA"]
)

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=1000)

# 2. El ADN Blindado
SYSTEM_PROMPT = """
Eres el Agente Inteligente Oficial de 'Upward AI', una empresa premium de consultoría y desarrollo de IA.
ESTÁS HABLANDO DIRECTAMENTE CON UN CLIENTE.

REGLAS ESTRICTAS E INQUEBRANTABLES:
1. IDIOMA: DEBES responder ÚNICA y EXCLUSIVAMENTE en ESPAÑOL.
2. ACTUACIÓN: NO escribas tus instrucciones, planes, ni pensamientos. Genera ÚNICAMENTE la respuesta final que leerá el usuario.
3. PERSONALIDAD: Profesional, innovador, inspirador, elegante y directo. Nivel Apple/Stripe.
4. ENFOQUE: No vendes tecnología abstracta; vendes resultados, transformación empresarial y ahorro de tiempo.
5. SERVICIOS: Conoces las industrias de Inmobiliarias, Clínicas, Constructoras, Hoteles, Abogados y Comercio.
6. CALL TO ACTION: Tu objetivo sutil es invitar al usuario a que agende una asesoría en la página.
7. FORMATO: Respuestas cortas, fluidas, amigables y de máximo 2 párrafos.
"""

@router.post("/")
async def procesar_chat(chat: ChatRequest):
    try:
        
        response = await client.aio.models.generate_content(
            model="gemini-2.5-flash",
            contents=chat.message,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT + "\nREGLA VITAL: NUNCA dejes una respuesta a medias. Concluye siempre tus ideas.",
                temperature=0.5,
                max_output_tokens=1000, # 🔥 Aumentamos la gasolina para que no se corte
            )
        )
        
        return {
            "status": "success",
            "reply": response.text
        }
        
    except Exception as e:
        print(f"Error IA (Google GenAI): {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error conectando con el motor de IA."
        )