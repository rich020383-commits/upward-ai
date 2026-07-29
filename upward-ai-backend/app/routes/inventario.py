from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
import csv
import io
from app.database import SessionLocal
from app import models

router = APIRouter(
    prefix="/api/inventario",
    tags=["Inventario de Comercios"]
)

class ProductoNuevo(BaseModel):
    tienda_id: str
    nombre: str
    precio: float
    categoria: Optional[str] = None
    disponible: bool = True

class ProductoEditar(BaseModel):
    nombre: str
    precio: float
    categoria: Optional[str] = None

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 1. RUTA PARA GUARDAR UN SOLO PRODUCTO A MANO
@router.post("/")
async def agregar_producto(producto: ProductoNuevo, db: Session = Depends(get_db)):
    nuevo_producto = models.Producto(
        tienda_id=producto.tienda_id,
        nombre=producto.nombre,
        precio=producto.precio,
        categoria=producto.categoria,
        disponible=producto.disponible
    )
    db.add(nuevo_producto)
    db.commit()
    return {"status": "success"}

# 2. RUTA PARA SUBIR EL INVENTARIO POR ARCHIVO CSV
@router.post("/cargar-csv/")
async def cargar_inventario_csv(
    tienda_id: str = Form(...),
    archivo: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    contenido = await archivo.read()
    texto = contenido.decode("utf-8")
    lector_csv = csv.DictReader(io.StringIO(texto))
    productos_agregados = 0
    
    for fila in lector_csv:
        try:
            nuevo_producto = models.Producto(
                tienda_id=tienda_id,
                nombre=fila.get("nombre", "Sin nombre").strip(),
                precio=float(fila.get("precio", 0)),
                categoria=fila.get("categoria", "General").strip(),
                disponible=True
            )
            db.add(nuevo_producto)
            productos_agregados += 1
        except Exception as e:
            print(f"Error saltando fila defectuosa: {e}")
            continue
            
    db.commit()
    return {"status": "success", "mensaje": f"¡{productos_agregados} productos cargados con éxito!"}

# 3. RUTA PARA CONSULTAR EL INVENTARIO (Actualizada con el ID)
@router.get("/{tienda_id}")
async def consultar_inventario(tienda_id: str, db: Session = Depends(get_db)):
    productos_db = db.query(models.Producto).filter(
        models.Producto.tienda_id == tienda_id,
        models.Producto.disponible == True
    ).all()

    # Ahora mandamos el 'id' para que Next.js sepa a quién editar o borrar
    lista_productos = [
        {"id": p.id, "nombre": p.nombre, "precio": p.precio, "categoria": p.categoria} 
        for p in productos_db
    ]

    return {
        "status": "success",
        "tienda_id": tienda_id,
        "inventario": lista_productos
    }

# 👇 4. NUEVA RUTA PARA EDITAR 👇
@router.put("/{producto_id}")
async def editar_producto(producto_id: int, producto_actualizado: ProductoEditar, db: Session = Depends(get_db)):
    producto_db = db.query(models.Producto).filter(models.Producto.id == producto_id).first()
    
    if not producto_db:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
        
    producto_db.nombre = producto_actualizado.nombre
    producto_db.precio = producto_actualizado.precio
    producto_db.categoria = producto_actualizado.categoria
    
    db.commit()
    return {"status": "success", "mensaje": "Producto actualizado"}

# 👇 5. NUEVA RUTA PARA ELIMINAR 👇
@router.delete("/{producto_id}")
async def eliminar_producto(producto_id: int, db: Session = Depends(get_db)):
    producto_db = db.query(models.Producto).filter(models.Producto.id == producto_id).first()
    
    if not producto_db:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
        
    db.delete(producto_db)
    db.commit()
    return {"status": "success", "mensaje": "Producto eliminado de los estantes"}