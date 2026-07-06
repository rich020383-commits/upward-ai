from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

router = APIRouter(
    prefix="/api/leads",
    tags=["Leads & Asesorías"]
)

# Esquema de validación de datos (Pydantic)
class LeadCreate(BaseModel):
    nombre_completo: str = Field(..., min_length=3, max_length=100, example="Andrés Mendoza")
    empresa: str = Field(..., min_length=2, max_length=100, example="Upward AI Corp")
    email: EmailStr = Field(..., example="andres@upwardai.com")
    telefono: str = Field(..., min_length=7, max_length=20, example="+573001234567")
    tamano_empresa: str = Field(..., example="11-50 empleados")
    mensaje: Optional[str] = Field(None, max_length=500, example="Queremos automatizar nuestro CRM con un agente de IA.")

@router.post("/", status_code=status.HTTP_201_CREATED)
async def registrar_lead(lead: LeadCreate):
    try:
        # Aquí más adelante conectaremos la Base de Datos o enviaremos un Webhook a Slack/CRM
        return {
            "status": "success",
            "message": "Solicitud de asesoría recibida correctamente.",
            "data": {
                "empresa": lead.empresa,
                "registro_at": datetime.utcnow().isoformat()
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno al procesar la solicitud: {str(e)}"
        )