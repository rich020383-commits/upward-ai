from sqlalchemy import Column, Integer, String, Float, Boolean, Text
from app.database import Base

class Producto(Base):
    __tablename__ = "productos"

    id = Column(Integer, primary_key=True, index=True)
    # tienda_id es la clave del modelo multi-tenant: 
    # Aquí guardamos el teléfono de la tienda o su ID, para que no se mezclen los huevos de la Tienda A con los de la Tienda B
    tienda_id = Column(String, index=True) 
    nombre = Column(String, index=True)
    precio = Column(Float)
    disponible = Column(Boolean, default=True) # Para que el tendero pueda pausar un producto sin borrarlo
    categoria = Column(String, nullable=True) # Ej: "Lácteos", "Aseo", "Granos"

# 👇 NUEVA TABLA PARA EL CEREBRO DEL BOT 👇
class ConfiguracionBot(Base):
    __tablename__ = "configuracion_bot"

    id = Column(Integer, primary_key=True, index=True)
    tienda_id = Column(String, unique=True, index=True) # unique=True para que haya 1 sola config por tienda
    nombre_agente = Column(String, default="Asistente Upway")
    prompt_maestro = Column(Text) # Usamos Text porque las reglas pueden ser muy largas

# 👇 NUEVA TABLA: CAJERO AUTOMÁTICO (PEDIDOS) 👇
class Pedido(Base):
    __tablename__ = "pedidos"

    id = Column(Integer, primary_key=True, index=True)
    tienda_id = Column(String, index=True)
    telefono_cliente = Column(String, index=True)
    resumen_productos = Column(String)  # Ej: "1x Queso, 2x Plátano"
    total = Column(Float)
    direccion_envio = Column(String, nullable=True)
    estado = Column(String, default="Pendiente") # Puede ser: Pendiente, Despachado, Cancelado