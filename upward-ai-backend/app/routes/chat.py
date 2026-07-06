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

SYSTEM_PROMPT = """
Eres el Agente Inteligente Oficial de 'Upward AI', una empresa premium de consultoría y desarrollo de IA.
ESTÁS HABLANDO DIRECTAMENTE CON UN CLIENTE.

REGLAS ESTRATÉGICAS DE CAPTACIÓN Y VENTAS:
1. PERFILAMIENTO: Tu objetivo es entender la necesidad del cliente, mostrar autoridad y convencerlo de agendar una demostración o asesoría.
2. NUNCA PIDAS DATOS: Por seguridad, NUNCA pidas nombre, correo, ni teléfono directamente en la conversación.
3. EL GATILLO FINAL: Cuando el cliente demuestre la intención de agendar (ej: "quiero agendar", "vamos", "me interesa", "ok quiero la cita"), DEBES finalizar tu respuesta EXACTAMENTE con esta etiqueta oculta: [ABRIR_FORMULARIO].
4. PERSONALIDAD: Profesional, directo, elegante. Nivel Apple/Stripe.
5. FORMATO: Respuestas cortas, fluidas, de máximo 2 párrafos.

Ejemplo de cierre exitoso:
"Excelente decisión. El siguiente paso es conectarte con uno de nuestros especialistas. Haz clic en el botón a continuación para registrar tu solicitud y agendar el espacio. [ABRIR_FORMULARIO]"
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
        # 🔥 EL ESCUDO ANTI-CAÍDAS: En lugar de un error 500, devolvemos una respuesta controlada
        print(f"Error IA (Google GenAI): {e}")
        return {
            "status": "error",
            "reply": "Estoy procesando un alto volumen de información en este momento. Por favor, dame unos segundos para estabilizar mi conexión y vuelve a escribirme."
        }