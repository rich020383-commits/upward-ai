import google.generativeai as genai
import os
from dotenv import load_dotenv

# Cargar las variables del .env
load_dotenv()
llave = os.getenv("GEMINI_API_KEY", "").strip().strip('"').strip("'")
genai.configure(api_key=llave)

print("\n🔍 Consultando a Google con tu llave...")
print("========================================")
print("Los modelos que SÍ puedes usar son:\n")

try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"✅ {m.name}")
    print("\n========================================")
except Exception as e:
    print(f"❌ Error de conexión con Google: {e}")