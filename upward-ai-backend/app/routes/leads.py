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

# Esquema de validación original para capturar los datos del prospecto[cite: 1]
class LeadCreate(BaseModel):
    nombre_completo: str = Field(..., min_length=3, max_length=100)
    empresa: str = Field(..., min_length=2, max_length=100)
    email: EmailStr = Field(...)
    telefono: str = Field(...)
    tamano_empresa: str = Field(...)
    mensaje: Optional[str] = Field(None)

@router.post("/", status_code=status.HTTP_201_CREATED)
async def registrar_lead(lead: LeadCreate):
    
    # 🔐 Leemos la llave secreta directamente desde la memoria segura de Render
    RESEND_API_KEY = os.getenv("RESEND_API_KEY") 
    
    REMITENTE = "notificaciones@upway.business" 
    CORREO_CENTRAL = "upwaybusiness@gmail.com"

    mensaje_texto = lead.mensaje if lead.mensaje else "No dejó mensaje adicional."

    # ==========================================
    # 1. PLANTILLA PARA EL CLIENTE FINAL
    # ==========================================
    html_cliente = f"""
    <div style="font-family: sans-serif; max-width: 600px; margin: auto; border: 1px solid #e2e8f0; border-radius: 10px; overflow: hidden;">
        <div style="background-color: #0f172a; padding: 20px; text-align: center; color: white;">
            <h2 style="margin: 0;">¡Hola {lead.nombre_completo}! Bienvenido a Upway</h2>
        </div>
        <div style="padding: 20px; background-color: #f8fafc; color: #334155;">
            <p>Hemos recibido correctamente tu solicitud para <strong>{lead.empresa}</strong>.</p>
            <p>Nuestro equipo de especialistas en automatización está analizando tu caso. Nos pondremos en contacto contigo pronto al número que nos proporcionaste ({lead.telefono}) para agendar nuestra primera sesión.</p>
            <p>Si tienes información adicional, puedes responder directamente a este correo.</p>
        </div>
        <div style="padding: 20px; text-align: center; font-size: 12px; color: #94a3b8; background-color: #ffffff;">
            <p>Upway Business - Liderando la innovación B2B</p>
        </div>
    </div>
    """

    # ==========================================
    # 2. PLANTILLA PARA TU EQUIPO (INTELIGENCIA B2B)
    # ==========================================
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
        <div style="padding: 20px; text-align: center; background-color: #ffffff;">
            <a href="https://wa.me/{lead.telefono.replace('+', '').replace(' ', '')}" 
               style="display: inline-block; background-color: #22c55e; color: white; padding: 12px 24px; text-decoration: none; border-radius: 8px; font-weight: bold; font-size: 16px;">
               Contactar por WhatsApp
            </a>
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
        requests.post(url, json=payload_cliente, headers=headers)
        requests.post(url, json=payload_admin, headers=headers)
        
        return {
            "status": "success",
            "message": "Correos de confirmación y notificación enviados exitosamente."
        }
            
    except Exception as e:
        print(f"Error crítico de conexión: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error de red al procesar las notificaciones."
        )