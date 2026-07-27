import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

router = APIRouter(
    prefix="/api/leads",
    tags=["Leads & Asesorías"]
)

# Esquema de validación de datos (Pydantic) - ¡Intacto con tu estructura original!
class LeadCreate(BaseModel):
    nombre_completo: str = Field(..., min_length=3, max_length=100, example="Andrés Mendoza")
    empresa: str = Field(..., min_length=2, max_length=100, example="Upway Business")
    email: EmailStr = Field(..., example="andres@upway.business")
    telefono: str = Field(..., min_length=7, max_length=20, example="+573001234567")
    tamano_empresa: str = Field(..., example="11-50 empleados")
    mensaje: Optional[str] = Field(None, max_length=500, example="Queremos automatizar nuestro CRM.")

@router.post("/", status_code=status.HTTP_201_CREATED)
async def registrar_lead(lead: LeadCreate):
    # 1. Configuración de tu servidor SMTP 
    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 587
    SENDER_EMAIL = "tu_correo@gmail.com"          # 👉 Pon tu correo aquí
    SENDER_PASSWORD = "dchy cfyj zxtp gfsv"       # 👉 Tu contraseña de aplicación (sin espacios si da error)
    RECEIVER_EMAIL = "tu_correo@gmail.com"        # 👉 El correo donde quieres que te lleguen las notificaciones

    # 2. Construcción del mensaje premium
    msg = MIMEMultipart()
    msg['From'] = f"Upway Business <{SENDER_EMAIL}>"
    msg['To'] = RECEIVER_EMAIL
    msg['Subject'] = f"🚨 NUEVO LEAD - UPWAY BUSINESS: {lead.nombre_completo} - {lead.empresa}"

    # Formateamos el mensaje incluyendo todos los campos de tu esquema
    mensaje_texto = lead.mensaje if lead.mensaje else "No dejó mensaje adicional."
    
    cuerpo_mensaje = f"""
    ¡Hola! Has recibido una nueva solicitud de servicio desde la plataforma oficial de Upway Business.

    --------------------------------------------------
    📌 DETALLES DEL PROSPECTO
    --------------------------------------------------
    👤 Nombre: {lead.nombre_completo}
    🏢 Empresa: {lead.empresa}
    ✉️ Correo: {lead.email}
    📞 Teléfono: {lead.telefono}
    👥 Tamaño de la empresa: {lead.tamano_empresa}
    💬 Mensaje/Requerimiento: {mensaje_texto}

    --------------------------------------------------
    ⚡ ACCIÓN RÁPIDA
    --------------------------------------------------
    Abrir chat directo en WhatsApp:
    https://wa.me/{lead.telefono.replace('+', '').replace(' ', '')}

    --
    Mensaje generado automáticamente por la infraestructura de Upway Business.
    """

    msg.attach(MIMEText(cuerpo_mensaje, 'plain', 'utf-8'))

    # 3. Envío seguro a través del servidor de Google
    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()  
        server.login(SENDER_EMAIL, SENDER_PASSWORD.replace(" ", "")) # Limpiamos espacios por si acaso
        server.send_message(msg)
        server.quit()
        
        # Respuesta de éxito manteniendo tu estructura exacta para el frontend
        return {
            "status": "success",
            "message": "Solicitud de asesoría recibida y enviada por correo exitosamente.",
            "data": {
                "empresa": lead.empresa,
                "registro_at": datetime.utcnow().isoformat()
            }
        }
    except Exception as e:
        print(f"Error crítico al enviar correo: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno al procesar la solicitud: {str(e)}"
        )