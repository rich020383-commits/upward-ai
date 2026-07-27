from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import leads  
from app.routes import chat 

# 1. PRIMERO creamos la variable app
app = FastAPI(
    title="Upway Business API",
    description="Backend de alto rendimiento para la automatización e integración de IA",
    version="1.0.0"
)

# 2. SEGUNDO configuramos los CORS
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://upward-ai-frontend.onrender.com", 
    "https://upway.business",      # 🔥 Tu nuevo dominio principal
    "https://www.upway.business"   # 🔥 Tu nuevo subdominio
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. TERCERO incluimos las rutas 
app.include_router(leads.router)
app.include_router(chat.router) 

@app.get("/")
def read_root():
    return {
        "brand": "Upway Business",
        "status": "Online",
        "version": "1.0.0",
        "environment": "Production"
    }