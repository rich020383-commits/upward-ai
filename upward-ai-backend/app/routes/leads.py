import os
import psycopg2
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

router = APIRouter(
    prefix="/api/leads",
    tags=["Leads & Asesorías"]
)

# Traemos la llave secreta desde el entorno (Render o local)
DATABASE_URL = os.getenv("DATABASE_URL")

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
        # 1. Abrimos conexión a la bóveda de Supabase
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()

        # 2. Preparamos la inyección de los datos en la tabla
        insert_query = """
        INSERT INTO leads (nombre_completo, empresa, email, telefono, tamano_empresa, mensaje)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        record_to_insert = (
            lead.nombre_completo, 
            lead.empresa, 
            lead.email, 
            lead.telefono, 
            lead.tamano_empresa, 
            lead.mensaje
        )

        # 3. Ejecutamos, guardamos y cerramos la puerta
        cursor.execute(insert_query, record_to_insert)
        conn.commit()
        
        cursor.close()
        conn.close()

        # Respuesta de éxito manteniendo tu estructura
        return {
            "status": "success",
            "message": "Solicitud de asesoría recibida y guardada correctamente en Supabase.",
            "data": {
                "empresa": lead.empresa,
                "registro_at": datetime.utcnow().isoformat()
            }
        }
    except Exception as e:
        print(f"Error guardando el lead: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno al procesar la solicitud: {str(e)}"
        )