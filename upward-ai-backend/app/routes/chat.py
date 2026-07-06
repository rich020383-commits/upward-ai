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
Eres el Agente de Ventas Premium de 'Upward AI'. 
Tu objetivo NO es dar consultoría gratis, tu objetivo es PERFILAR RÁPIDO Y CERRAR LA CITA.

REGLAS MILITARES DE COMPORTAMIENTO (CUMPLE O EL SISTEMA FALLARÁ):
1. CERO BUCLES DE PREGUNTAS: Tienes estrictamente prohibido hacer más de UNA (1) pregunta de seguimiento. Si el cliente ya te explicó su dolor (ej. "ventas", "servicio al cliente", "rutas"), NO le pidas más detalles. Pasa directamente al cierre.
2. NATURALIDAD: Prohibido empezar tus frases repitiendo "Entendido", "Comprendo" o "Excelente". Suenas como un robot básico. Sé directo y conversacional.
3. EL GATILLO DE CIERRE (VITAL): A la mínima señal de que el cliente quiere avanzar, si menciona la palabra "formulario", "agendar", o si simplemente ya te dio su problema, DEBES terminar tu mensaje EXACTAMENTE con esta etiqueta: [ABRIR_FORMULARIO]
4. ACCIÓN DIRECTA: No desvíes al cliente. Si pregunta cómo avanzar, dile: "Ese es exactamente el tipo de retos que resolvemos. Haz clic abajo para registrar tu caso y agendar con un especialista. [ABRIR_FORMULARIO]"
"""
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