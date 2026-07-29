from app.database import SessionLocal
from app.models import Producto

# 1. Abrimos la conexión con la base de datos
db = SessionLocal()

# 2. Creamos los productos para una tienda de prueba (ej. teléfono 3001234567)
producto1 = Producto(
    tienda_id="3001234567",
    nombre="Paca de Leche Entera",
    precio=42000.0,
    disponible=True,
    categoria="Lácteos"
)

producto2 = Producto(
    tienda_id="3001234567",
    nombre="Cubeta de Huevos AA",
    precio=18500.0,
    disponible=True,
    categoria="Canasta Familiar"
)

# 3. Le decimos a la base de datos que los guarde
try:
    db.add(producto1)
    db.add(producto2)
    db.commit()
    print("¡Magia hecha! 🚀 Productos inyectados con éxito en la base de datos.")
except Exception as e:
    print(f"Hubo un error: {e}")
finally:
    # 4. Cerramos la puerta al salir
    db.close()