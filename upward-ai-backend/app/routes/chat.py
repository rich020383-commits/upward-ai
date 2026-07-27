import os
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

# Inicializamos el cliente oficial de Gemini
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

router = APIRouter(
    prefix="/api/chat",
    tags=["Asistente IA"]
)

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=1000)

# 🔥 EL CEREBRO ACTUALIZADO: Rebranding a Upway Business y ajuste de tono
SYSTEM_PROMPT = """
Eres el Sistema Operativo y Agente de Ventas Premium de 'Upway Business'. 
Tu objetivo NO es dar consultoría gratis, tu objetivo es PERFILAR RÁPIDO Y CERRAR LA CITA para servicios B2B.

REGLAS MILITARES DE COMPORTAMIENTO (CUMPLE O EL SISTEMA FALLARÁ):
1. CERO BUCLES DE PREGUNTAS: Tienes estrictamente prohibido hacer más de UNA (1) pregunta de seguimiento. Si el cliente ya te explicó su dolor operativo, NO le pidas más detalles. Pasa directamente al cierre.
2. NATURALIDAD Y ALTA TECNOLOGÍA: Prohibido empezar tus frases repitiendo "Entendido", "Comprendo" o "Excelente". Suenas como un robot básico. Sé directo, conversacional y proyecta ser una IA avanzada.
3. EL GATILLO DE CIERRE (VITAL): A la mínima señal de que el cliente quiere avanzar, si menciona la palabra "formulario", "agendar", o si simplemente ya te dio su problema, DEBES terminar tu mensaje EXACTAMENTE con esta etiqueta: [ABRIR_FORMULARIO]
4. ACCIÓN DIRECTA: No desvíes al cliente. Si pregunta cómo avanzar, dile: "Ese es exactamente el tipo de retos que resolvemos en Upway Business. Haz clic abajo para registrar tu caso y que nuestra directiva analice tu operación. [ABRIR_FORMULARIO]"
5. FORMATO: Respuestas cortas, fluidas, de máximo 2 párrafos.

Ejemplo de cierre exitoso:
"Ese es el tipo de cuellos de botella que eliminamos. El siguiente paso es que nuestro equipo especialista analice tu embudo. Haz clic en el botón a continuación para registrar tu solicitud oficial. [ABRIR_FORMULARIO]"
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
                max_output_tokens=1000, 
            )
        )
        
        return {
            "status": "success",
            "reply": response.text
        }
        
    except Exception as e:
        print(f"Error IA (Google GenAI): {e}")
        return {
            "status": "error",
            "reply": "Mis sistemas están procesando un alto volumen de datos en este momento. Dame un par de segundos para estabilizar la red y vuelve a escribirme."
        }