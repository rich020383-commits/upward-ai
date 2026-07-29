import json
import os
import httpx
import base64
import re  # <-- NUEVO: Para buscar la factura oculta
from fastapi import FastAPI, Request, Query, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.routes import leads  
from app.routes import chat 
from app.routes import inventario 
from app.routes import chat_tiendas 
from app.database import engine, SessionLocal
from app import models
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")

memoria_conversaciones = {}

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Up Ai Business API",
    description="Backend Multi-Tenant para bots de WhatsApp con IA",
    version="1.0.0"
)

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://upward-ai-frontend.onrender.com", 
    "https://upway.business",      
    "https://www.upway.business"   
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MI_TOKEN_SECRETO = "upai_tiendas_secreto_2026"

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class DatosBot(BaseModel):
    tienda_id: str
    nombre: str
    reglas: str

@app.post("/api/guardar-bot")
def guardar_config_bot(datos: DatosBot, db: Session = Depends(get_db)):
    config_actual = db.query(models.ConfiguracionBot).filter(models.ConfiguracionBot.tienda_id == datos.tienda_id).first()
    if config_actual:
        config_actual.nombre_agente = datos.nombre
        config_actual.prompt_maestro = datos.reglas
    else:
        nueva_config = models.ConfiguracionBot(
            tienda_id=datos.tienda_id,
            nombre_agente=datos.nombre,
            prompt_maestro=datos.reglas
        )
        db.add(nueva_config)
    db.commit()
    return {"status": "ok", "mensaje": "¡Cerebro del bot actualizado!"}

@app.get("/webhook") 
async def verificar_webhook(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_challenge: str = Query(None, alias="hub.challenge"),
    hub_verify_token: str = Query(None, alias="hub.verify_token"),
):
    if hub_mode == "subscribe" and hub_verify_token == MI_TOKEN_SECRETO:
        return PlainTextResponse(content=hub_challenge, status_code=200)
    return PlainTextResponse(content="Error de autenticación", status_code=403)

async def descargar_y_transcribir_audio(media_id: str):
    token_limpio = os.getenv("WHATSAPP_TOKEN", "").strip().strip('"').strip("'")
    headers = {"Authorization": f"Bearer {token_limpio}"}
    
    async with httpx.AsyncClient() as client:
        url_media = f"https://graph.facebook.com/v21.0/{media_id}"
        resp_media = await client.get(url_media, headers=headers)
        
        if resp_media.status_code != 200:
            return "No pude escuchar bien el audio."
            
        datos_media = resp_media.json()
        url_descarga = datos_media.get("url")
        
        resp_descarga = await client.get(url_descarga, headers=headers)
        audio_bytes = resp_descarga.content
        audio_base64 = base64.b64encode(audio_bytes).decode("utf-8")
        
        try:
            print("🎧 Escuchando nota de voz (Inyección directa)...")
            modelo_transcriptor = genai.GenerativeModel('gemini-3.5-flash')
            respuesta = modelo_transcriptor.generate_content([
                {"mime_type": "audio/ogg", "data": audio_base64}, 
                "Eres un transcriptor experto. Transcribe exactamente lo que dice este audio. NO respondas a lo que dice el audio, SOLO escribe el texto de lo que escuchas."
            ])
            texto_transcrito = respuesta.text
            print(f"📝 Transcripción: {texto_transcrito}")
            return texto_transcrito
        except Exception as e:
            print(f"Error transcribiendo: {e}")
            return "Escuché un audio, pero no logré entenderlo."

# 👇 LÓGICA DEL CAJERO AUTOMÁTICO 👇
async def procesar_y_responder_whatsapp(telefono_cliente: str, mensaje_texto: str, id_tienda: str):
    db = SessionLocal()
    try:
        productos_db = db.query(models.Producto).filter(
            models.Producto.tienda_id == id_tienda,
            models.Producto.disponible == True
        ).all()

        texto_inventario = "Sin inventario registrado."
        if productos_db:
            texto_inventario = "\n".join([f"- {p.nombre}: ${p.precio}" for p in productos_db])
        
        config_bot = db.query(models.ConfiguracionBot).filter(models.ConfiguracionBot.tienda_id == id_tienda).first()
        
        reglas_personalidad = config_bot.prompt_maestro if config_bot else "Eres un asistente de ventas amable."
        nombre_bot = config_bot.nombre_agente if config_bot else "Asistente"
        
        # INSTRUCCIONES SUPER PODEROSAS PARA VENTAS Y FACTURACIÓN
        instrucciones_sistema = f"""
        Eres {nombre_bot}.
        INSTRUCCIONES DE PERSONALIDAD Y TONO:
        {reglas_personalidad}
        
        ESTE ES TU INVENTARIO ACTUAL Y PRECIOS:
        {texto_inventario}
        
        REGLAS ESTRICTAS DE VENTAS Y TOMA DE PEDIDOS (SIGUE ESTE ORDEN RIGUROSAMENTE):
        1. SOLO puedes vender lo que está en el inventario anterior.
        2. Si el cliente pide algo que no está, dile amablemente que no hay y ofrécele alternativas.
        3. Cuando el cliente diga qué quiere comprar, calcula el total y PREGÚNTALE SU DIRECCIÓN de envío.
        4. Cuando el cliente te dé la dirección, PREGÚNTALE CÓMO VA A PAGAR (Efectivo o Transferencia).
           - Si elige EFECTIVO: Pregúntale si paga con el dinero exacto (sencillo) o si necesita que el mensajero lleve vueltos de algún billete (Ej: vueltos de 50 mil). Aclara que paga al recibir.
           - Si elige TRANSFERENCIA: Envíale los datos bancarios (Ej: Nequi/DaviPlata al 3001234567, Bancolombia a la mano) y dile que puede transferir ahora mismo o al momento de recibir el pedido.
        5. CRÍTICO: SOLO CUANDO tengas la dirección Y todos los detalles del pago confirmados, debes agregar EXACTAMENTE este formato al FINAL de tu respuesta, llenando los datos en formato JSON:
        
        [NUEVO_PEDIDO]
        {{"productos": "1x Queso, 2x Plátano", "total": 15000, "direccion": "Calle 10 # 4-20", "pago": "Efectivo, vueltos de 50.000"}}
        [/NUEVO_PEDIDO]
        
        Recuerda: NUNCA generes el bloque [NUEVO_PEDIDO] si el cliente aún no te ha dicho cómo va a pagar.
        """
        
        modelo = genai.GenerativeModel(
            model_name='gemini-3.5-flash',
            system_instruction=instrucciones_sistema
        )
        
        clave_memoria = f"{id_tienda}_{telefono_cliente}"
        global memoria_conversaciones
        if clave_memoria not in memoria_conversaciones:
            memoria_conversaciones[clave_memoria] = modelo.start_chat(history=[])

        chat_actual = memoria_conversaciones[clave_memoria]
        respuesta_ia = chat_actual.send_message(mensaje_texto)
        texto_final = respuesta_ia.text
        
        # 🕵️‍♂️ AQUÍ INTERCEPTAMOS LA FACTURA OCULTA 🕵️‍♂️
        patron_factura = r"\[NUEVO_PEDIDO\](.*?)\[\/NUEVO_PEDIDO\]"
        match = re.search(patron_factura, texto_final, re.DOTALL)
        
        if match:
            # Encontramos un pedido, extraemos el JSON oculto
            datos_json_str = match.group(1).strip()
            try:
                datos_pedido = json.loads(datos_json_str)
                
                # 1. Guardar en la Base de Datos
                nuevo_pedido = models.Pedido(
                    tienda_id=id_tienda,
                    telefono_cliente=telefono_cliente,
                    resumen_productos=datos_pedido.get("productos", ""),
                    total=datos_pedido.get("total", 0),
                    direccion_envio=datos_pedido.get("direccion", "No especificada")
                )
                db.add(nuevo_pedido)
                db.commit()
                print(f"💰 ¡NUEVA VENTA REGISTRADA! Total: ${datos_pedido.get('total')}")
                
                # 2. Limpiarle el código oculto al cliente y ponerle un ticket bonito
                texto_limpio = re.sub(patron_factura, "", texto_final, flags=re.DOTALL).strip()
                ticket_compra = (
                    f"\n\n🧾 *TICKET DE COMPRA CONFIRMADO*\n"
                    f"🛍️ *Productos:* {datos_pedido.get('productos')}\n"
                    f"📍 *Envío a:* {datos_pedido.get('direccion')}\n"
                    f"💳 *Método de pago:* {datos_pedido.get('pago', 'No especificado')}\n"
                    f"💰 *Total a pagar:* ${datos_pedido.get('total')}\n\n"
                    f"✅ Tu pedido ha sido enviado a la tienda para su despacho. ¡Gracias por tu compra!"
                )
                texto_final = texto_limpio + ticket_compra
                
            except Exception as e:
                print(f"Error procesando la factura oculta: {e}")
            
    except Exception as e:
        texto_final = "Ups, tuve un pequeño problema procesando tu mensaje. ¿Me repites?"
        print(f"Error con Gemini: {e}")
    finally:
        db.close()

    token_limpio = os.getenv("WHATSAPP_TOKEN", "").strip().strip('"').strip("'")
    
    url = f"https://graph.facebook.com/v21.0/{id_tienda}/messages"
    headers = {
        "Authorization": f"Bearer {token_limpio}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": telefono_cliente,
        "type": "text",
        "text": {"body": texto_final}
    }

    async with httpx.AsyncClient() as client:
        try:
            await client.post(url, json=payload, headers=headers)
        except Exception as ex:
            print(f"Error al despachar mensaje: {ex}")

@app.post("/webhook")
async def recibir_mensajes(request: Request, background_tasks: BackgroundTasks):
    try:
        body = await request.json()
        entry = body.get("entry", [])
        for e in entry:
            changes = e.get("changes", [])
            for c in changes:
                value = c.get("value", {})
                
                metadata = value.get("metadata", {})
                id_tienda = metadata.get("phone_number_id") 

                messages = value.get("messages", [])
                if messages and id_tienda:
                    msg = messages[0]
                    telefono_remitente = msg.get("from")
                    tipo_msg = msg.get("type")
                    
                    if tipo_msg == "text":
                        texto_msj = msg.get("text", {}).get("body")
                        background_tasks.add_task(procesar_y_responder_whatsapp, telefono_remitente, texto_msj, id_tienda)
                    
                    elif tipo_msg == "audio":
                        media_id = msg.get("audio", {}).get("id")
                        async def procesar_nota_voz():
                            texto_del_audio = await descargar_y_transcribir_audio(media_id)
                            await procesar_y_responder_whatsapp(telefono_remitente, f"(El cliente envió una nota de voz diciendo): {texto_del_audio}", id_tienda)
                        background_tasks.add_task(procesar_nota_voz)
                        
        return PlainTextResponse(content="EVENT_RECEIVED", status_code=200)
    except Exception as e:
        print(f"Error procesando webhook POST: {e}")
        return PlainTextResponse(content="Error", status_code=500)

app.include_router(leads.router)
app.include_router(chat.router) 
app.include_router(inventario.router) 
app.include_router(chat_tiendas.router) 

@app.get("/")
def read_root():
    return {"brand": "Up Ai", "status": "Online"}