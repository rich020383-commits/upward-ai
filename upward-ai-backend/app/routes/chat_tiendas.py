from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app import models
import google.generativeai as genai
import os
from dotenv import load_dotenv

# Cargamos las variables de entorno (tu API Key de Gemini)
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

router = APIRouter(
    prefix="/api/chat/tiendas",
    tags=["Bot Multitienda"]
)

# Dependencia para abrir y cerrar la base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Estructura del mensaje que recibiremos (simulando WhatsApp)
class MensajeCliente(BaseModel):
    tienda_id: str
    numero_cliente: str
    mensaje: str

@router.post("/recibir")
async def procesar_mensaje_tienda(datos: MensajeCliente, db: Session = Depends(get_db)):
    # 1. AISLAMIENTO: Buscamos SOLO el inventario de esta tienda específica
    productos_db = db.query(models.Producto).filter(
        models.Producto.tienda_id == datos.tienda_id,
        models.Producto.disponible == True
    ).all()

    # Si la tienda no tiene productos, atajamos el error rápido
    if not productos_db:
        return {"respuesta_bot": "Hola, en este momento estamos actualizando nuestro inventario. ¡Vuelve pronto!"}

    # 2. PREPARACIÓN: Convertimos los productos en un texto fácil de leer para Gemini
    texto_inventario = "\n".join([f"- {p.nombre}: ${p.precio}" for p in productos_db])

    # 3. EL CEREBRO: Armamos el "System Prompt" o paquete hermético
    prompt_maestro = f"""
    Eres el asistente virtual de ventas de un minimercado local.
    Tu objetivo es atender al cliente de forma amable, coloquial y directa.
    
    ESTE ES TU INVENTARIO ACTUAL Y PRECIOS:
    {texto_inventario}
    
    REGLAS ESTRICTAS:
    1. SOLO puedes vender lo que está en el inventario anterior.
    2. Si el cliente pide algo que no está en la lista, dile amablemente que no hay y ofrécele algo del inventario.
    3. Si el cliente hace un pedido, suma los precios y dale el total a pagar.
    
    MENSAJE DEL CLIENTE: "{datos.mensaje}"
    
    Escribe tu respuesta exacta para enviarla por WhatsApp:
    """

    # 4. LA MAGIA: Llamamos a Gemini con el modelo más rápido
    try:
        modelo = genai.GenerativeModel('gemini-2.5-flash')
        respuesta_ia = modelo.generate_content(prompt_maestro)
        texto_final = respuesta_ia.text
    except Exception as e:
        texto_final = "Ups, el de la caja se fue a almorzar. ¿Me repites tu pedido en un momento?"
        print(f"Error con Gemini: {e}")

    # 5. EL RETORNO: Devolvemos la respuesta lista para WhatsApp
    return {
        "status": "success",
        "tienda_id": datos.tienda_id,
        "respuesta_bot": texto_final
    }