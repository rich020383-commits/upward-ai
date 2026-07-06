import openai
from app.config import settings

class AIEngine:
    def __init__(self):
        # Inicializamos el cliente de OpenAI usando la API Key de la configuración
        if settings.OPENAI_API_KEY and settings.OPENAI_API_KEY != "tu-api-key-de-openai-aqui":
            openai.api_key = settings.OPENAI_API_KEY
        
        # El Prompt del Sistema define la identidad corporativa estricta de Upward AI
        self.system_prompt = (
            "Eres el Agente Inteligente oficial de UPWARD AI, una empresa líder especializada "
            "en soluciones de Inteligencia Artificial para negocios, emprendedores y empresas en Latinoamérica. "
            "Tu objetivo principal es ayudar a los visitantes a entender cómo la IA puede transformar "
            "su productividad y competitividad.\n\n"
            "FILOSOFÍA Y DIRECTRICES DE CONVERSACIÓN:\n"
            "- No vendes tecnología abstracta; vendes transformación empresarial y resultados reales "
            "(ahorro de tiempo, reducción de costos, aumento de ventas, optimización de procesos).\n"
            "- Tu tono es premium, moderno, elegante, altamente profesional, pero cercano y confiable.\n"
            "- La IA no reemplaza a las personas; potencia su talento.\n\n"
            "FUNCIONES CLAVE:\n"
            "1. Explicar servicios (Automatización de procesos, agentes inteligentes, chatbots personalizados, marketing/ventas).\n"
            "2. Recomendar soluciones adaptadas a industrias (Inmobiliarias, constructoras, clínicas, restaurantes, etc.).\n"
            "3. Cuando un cliente muestre interés real en una solución, solicita de forma natural sus datos "
            "(Nombre, Empresa, Correo, WhatsApp y qué desea automatizar) para agendar una consultoría estratégica.\n\n"
            "Mantén tus respuestas claras, dinámicas y estructuradas con viñetas cuando sea necesario. Evita bloques densos de texto."
        )

    async def generar_respuesta_stream(self, historial_mensajes: list):
        """
        Genera respuestas usando streaming para que el texto aparezca letra por letra en el frontend.
        """
        if not settings.OPENAI_API_KEY or settings.OPENAI_API_KEY == "tu-api-key-de-openai-aqui":
            # Retorno amigable en caso de que aún no configures la API Key real
            yield "¡Hola! Soy el Agente de Upward AI. El backend está conectado correctamente, pero necesitas configurar una OPENAI_API_KEY válida en tu archivo .env para que pueda empezar a asesorarte como un experto."
            return

        # Preparamos el payload incluyendo el prompt del sistema al inicio
        messages = [{"role": "system", "content": self.system_prompt}]
        messages.extend(historial_mensajes)

        try:
            response = await openai.ChatCompletion.acreate(
                model="gpt-4o-mini",  # Modelo rápido, económico y extremadamente inteligente
                messages=messages,
                stream=True,
                temperature=0.7
            )
            
            async for chunk in response:
                choice = chunk.choices[0]
                if "delta" in choice and "content" in choice.delta:
                    yield choice.delta.content
                    
        except Exception as e:
            yield f"Error en el motor de IA: {str(e)}"

# Instancia global del motor lista para ser usada en las rutas
ai_engine = AIEngine()