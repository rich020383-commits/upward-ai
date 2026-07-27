import os
import requests
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

router = APIRouter(
    prefix="/api/leads",
    tags=["Leads & Asesorías"]
)

class LeadCreate(BaseModel):
    nombre_completo: str = Field(..., min_length=3, max_length=100)
    empresa: str = Field(..., min_length=2, max_length=100)
    email: EmailStr = Field(...)
    telefono: str = Field(...)
    tamano_empresa: str = Field(...)
    mensaje: Optional[str] = Field(None)

@router.post("/", status_code=status.HTTP_201_CREATED)
async def registrar_lead(lead: LeadCreate):
    
    # 🔐 Leemos la llave secreta desde las variables de entorno de Render
    RESEND_API_KEY = os.getenv("RESEND_API_KEY") 
    
    if not RESEND_API_KEY:
        print("❌ ERROR CRÍTICO: La variable RESEND_API_KEY no está configurada en el servidor.")
        raise HTTPException(status_code=500, detail="Error de configuración del servidor (API Key faltante).")

    REMITENTE = "notificaciones@upway.business" 
    CORREO_CENTRAL = "upwaybusiness@gmail.com"
    mensaje_texto = lead.mensaje if lead.mensaje else "No dejó mensaje adicional."

    html_cliente = f"""
    <div style="font-family: sans-serif; max-width: 600px; margin: auto; border: 1px solid #e2e8f0; border-radius: 10px; overflow: hidden;">
        <div style="background-color: #0f172a; padding: 20px; text-align: center; color: white;">
            <h2 style="margin: 0;">¡Hola {lead.nombre_completo}! Bienvenido a Upway</h2>
        </div>
        <div style="padding: 20px; background-color: #f8fafc; color: #334155;">
            <p>Hemos recibido correctamente tu solicitud para <strong>{lead.empresa}</strong>.</p>
            <p>Nuestro equipo de especialistas en automatización está analizando tu caso. Nos pondremos en contacto contigo pronto al número que nos proporcionaste ({lead.telefono}).</p>
        </div>
    </div>
    """

    html_admin = f"""
    <div style="font-family: sans-serif; max-width: 600px; margin: auto; border: 1px solid #e2e8f0; border-radius: 10px; overflow: hidden;">
        <div style="background-color: #2563eb; padding: 20px; text-align: center; color: white;">
            <h2 style="margin: 0;">🚨 NUEVO LEAD B2B CAPTURADO</h2>
        </div>
        <div style="padding: 20px; background-color: #f8fafc; color: #334155;">
            <p><strong>👤 Nombre:</strong> {lead.nombre_completo}</p>
            <p><strong>🏢 Empresa:</strong> {lead.empresa}</p>
            <p><strong>✉️ Correo:</strong> {lead.email}</p>
            <p><strong>📞 Teléfono:</strong> {lead.telefono}</p>
            <p><strong>👥 Tamaño:</strong> {lead.tamano_empresa}</p>
            <p><strong>💬 Mensaje:</strong> {mensaje_texto}</p>
        </div>
    </div>
    """

    url = "https://api.resend.com/emails"
    headers = {
        "Authorization": f"Bearer {RESEND_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload_cliente = {
        "from": f"Upway Business <{REMITENTE}>",
        "to": [lead.email],
        "subject": "Hemos recibido tu solicitud - Upway Business",
        "html": html_cliente
    }

    payload_admin = {
        "from": f"Sistema Upway <{REMITENTE}>",
        "to": [CORREO_CENTRAL],
        "subject": f"🎯 NUEVO PROSPECTO: {lead.nombre_completo} - {lead.empresa}",
        "html": html_admin
    }

    try:
        # Enviamos y evaluamos la respuesta de Resend para el cliente
        res_cliente = requests.post(url, json=payload_cliente, headers=headers)
        print("📨 Respuesta Resend (Cliente):", res_cliente.status_code, res_cliente.text)

        # Enviamos y evaluamos la respuesta de Resend para el admin
        res_admin = requests.post(url, json=payload_admin, headers=headers)
        print("📨 Respuesta Resend (Admin):", res_admin.status_code, res_admin.text)

        if res_cliente.status_code not in [200, 201] or res_admin.status_code not in [200, 201]:
            raise HTTPException(
                status_code=500, 
                detail=f"Resend rechazó el envío. Revisa los logs de Render."
            )
        
        return {
            "status": "success",
            "message": "Correos procesados correctamente."
        }
            
    except Exception as e:
        print(f"❌ Error crítico procesando correos: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )