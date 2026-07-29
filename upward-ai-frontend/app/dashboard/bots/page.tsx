"use client";

import React, { useState } from 'react';

export default function AgentesBotPage() {
  // 1. Creamos las memorias temporales para los inputs
  const [nombreAgente, setNombreAgente] = useState('');
  const [promptMaestro, setPromptMaestro] = useState('');
  const [guardando, setGuardando] = useState(false);

  // 2. Función que se ejecuta al darle clic al botón (CONEXIÓN REAL A PYTHON)
  const guardarConfiguracion = async () => {
    if (!nombreAgente || !promptMaestro) {
      alert("⚠️ Hermano, llena el nombre y las reglas antes de guardar.");
      return;
    }

    setGuardando(true);
    
    // Empaquetamos los datos tal cual los pide Pydantic en tu backend
    const datosParaBackend = {
      tienda_id: "1172769935927318", // El ID interno de Meta inyectado correctamente
      nombre: nombreAgente,
      reglas: promptMaestro
    };
    
    try {
      // Disparamos el misil hacia tu backend en FastAPI
      const respuesta = await fetch("http://localhost:8000/api/guardar-bot", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(datosParaBackend),
      });

      if (respuesta.ok) {
        const resultado = await respuesta.json();
        console.log("Respuesta del servidor:", resultado);
        alert("✅ ¡Cerebro del bot actualizado en la base de datos con éxito!");
      } else {
        alert("❌ Hubo un problema al guardar. Revisa la consola.");
      }
    } catch (error) {
      console.error("Error conectando con FastAPI:", error);
      alert("❌ El frontend no pudo alcanzar al backend. ¿Está encendido Uvicorn?");
    } finally {
      setGuardando(false);
    }
  };

  return (
    <div className="p-8 max-w-7xl mx-auto bg-gray-50 min-h-screen font-sans">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 tracking-tight">Agentes Bot de Upway</h1>
        <p className="text-gray-500 mt-2 text-sm">Configura la personalidad, reglas y base de conocimiento de tu asistente de inteligencia artificial.</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Columna Izquierda: Configuración (2/3 del espacio) */}
        <div className="lg:col-span-2 space-y-6">
          
          {/* Tarjeta 1: Entrenamiento */}
          <div className="bg-white p-6 rounded-2xl border border-gray-200 shadow-sm">
            <div className="flex items-center gap-3 mb-6">
              <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center text-blue-600 font-bold">1</div>
              <h2 className="text-xl font-semibold text-gray-800">Personalidad y Reglas</h2>
            </div>
            
            <div className="space-y-5">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Nombre del Agente</label>
                <input 
                  type="text" 
                  value={nombreAgente}
                  onChange={(e) => setNombreAgente(e.target.value)}
                  placeholder="Ej. Asistente Upway" 
                  className="w-full border border-gray-300 rounded-xl p-3 focus:ring-2 focus:ring-blue-500 outline-none transition-all text-sm"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Instrucciones del Prompt Maestro</label>
                <textarea 
                  value={promptMaestro}
                  onChange={(e) => setPromptMaestro(e.target.value)}
                  placeholder="Escribe aquí las reglas estrictas (ej. No dar descuentos, saludar formalmente)..." 
                  className="w-full border border-gray-300 rounded-xl p-3 h-40 focus:ring-2 focus:ring-blue-500 outline-none transition-all text-sm resize-none"
                ></textarea>
              </div>
            </div>
          </div>

          {/* Tarjeta 2: Base de Conocimiento */}
          <div className="bg-white p-6 rounded-2xl border border-gray-200 shadow-sm">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center text-blue-600 font-bold">2</div>
              <h2 className="text-xl font-semibold text-gray-800">Cerebro (Base de Conocimiento)</h2>
            </div>
            <p className="text-sm text-gray-500 mb-6">Conecta tu inventario o sube documentos para que la IA sepa exactamente qué responder y qué vender.</p>
            
            <button className="w-full border-2 border-dashed border-gray-300 text-gray-500 px-4 py-12 rounded-xl text-center hover:bg-blue-50 hover:border-blue-300 hover:text-blue-600 transition-all font-medium flex flex-col items-center justify-center gap-2">
              <span className="text-2xl">📦</span>
              Sincronizar Inventario de la Base de Datos
            </button>
          </div>
        </div>

        {/* Columna Derecha: Monitor (1/3 del espacio) */}
        <div className="lg:col-span-1">
          <div className="bg-white p-6 rounded-2xl border border-gray-200 shadow-sm h-full flex flex-col">
            <div className="flex items-center gap-3 mb-6">
              <div className="w-8 h-8 rounded-full bg-green-100 flex items-center justify-center text-green-600 font-bold">3</div>
              <h2 className="text-xl font-semibold text-gray-800">Inbox en Vivo</h2>
            </div>
            
            <div className="flex-grow bg-gray-50 rounded-xl border border-gray-200 p-6 flex flex-col items-center justify-center text-center">
              <span className="text-5xl mb-4 opacity-50">📱</span>
              <p className="text-sm text-gray-600 font-medium">Esperando mensajes entrantes...</p>
              <p className="text-xs text-gray-400 mt-2">Aquí verás los chats de WhatsApp en tiempo real cuando tus clientes escriban.</p>
            </div>
            
            <button 
              onClick={guardarConfiguracion}
              disabled={guardando}
              className={`mt-6 w-full font-medium py-3 rounded-xl transition-all shadow-md ${
                guardando 
                  ? 'bg-blue-400 cursor-not-allowed text-white' 
                  : 'bg-blue-600 hover:bg-blue-700 text-white hover:shadow-lg'
              }`}
            >
              {guardando ? 'Guardando...' : 'Guardar y Activar Bot'}
            </button>
          </div>
        </div>

      </div>
    </div>
  );
}