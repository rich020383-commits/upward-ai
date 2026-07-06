from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import leads  
from app.routes import chat 

# 1. PRIMERO creamos la variable app
app = FastAPI(
    title="Upward AI API",
    description="Backend de alto rendimiento para la automatización e integración de IA",
    version="1.0.0"
)

# 2. SEGUNDO configuramos los CORS
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. TERCERO incluimos las rutas (ahora sí funciona porque app ya existe)
app.include_router(leads.router)
app.include_router(chat.router) # ← Lo movimos para acá abajo

@app.get("/")
def read_root():
    return {
        "brand": "Upward AI",
        "status": "Online",
        "version": "1.0.0",
        "environment": "Development"
    }