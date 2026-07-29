"use client";

import React, { useState, useEffect } from 'react';

export default function InventarioPage() {
  const [modoCarga, setModoCarga] = useState<'manual' | 'csv'>('manual');
  const [guardando, setGuardando] = useState(false);
  const [productos, setProductos] = useState<any[]>([]);
  const [cargando, setCargando] = useState(true);

  // Estados Manual
  const [nombre, setNombre] = useState('');
  const [precio, setPrecio] = useState('');
  const [categoria, setCategoria] = useState('');
  
  // Estado CSV
  const [archivoCSV, setArchivoCSV] = useState<File | null>(null);

  // Estados de Edición
  const [editandoId, setEditandoId] = useState<number | null>(null);
  const [editNombre, setEditNombre] = useState('');
  const [editPrecio, setEditPrecio] = useState('');
  const [editCategoria, setEditCategoria] = useState('');

  const TIENDA_ID = "1172769935927318"; 

  const cargarInventario = async () => {
    setCargando(true);
    try {
      const respuesta = await fetch(`http://localhost:8000/api/inventario/${TIENDA_ID}`);
      if (respuesta.ok) {
        const datos = await respuesta.json();
        setProductos(datos.inventario || []);
      }
    } catch (error) {
      console.error("Error", error);
    } finally {
      setCargando(false);
    }
  };

  useEffect(() => {
    cargarInventario();
  }, []);

  // Función Guardar Manual
  const agregarProducto = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!nombre || !precio) return alert("Nombre y precio son obligatorios.");
    setGuardando(true);
    
    try {
      const respuesta = await fetch("http://localhost:8000/api/inventario/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ tienda_id: TIENDA_ID, nombre, precio: parseFloat(precio), categoria: categoria || "General", disponible: true }),
      });
      if (respuesta.ok) {
        setNombre(''); setPrecio(''); setCategoria('');
        cargarInventario();
      }
    } catch (error) {
      alert("❌ Error conectando al servidor.");
    } finally {
      setGuardando(false);
    }
  };

  // Función Subir CSV
  const subirArchivoCSV = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!archivoCSV) return alert("Selecciona un archivo CSV primero.");
    setGuardando(true);

    const formData = new FormData();
    formData.append("tienda_id", TIENDA_ID);
    formData.append("archivo", archivoCSV);

    try {
      const respuesta = await fetch("http://localhost:8000/api/inventario/cargar-csv/", {
        method: "POST",
        body: formData, 
      });
      if (respuesta.ok) {
        setArchivoCSV(null);
        cargarInventario();
      } else {
        alert("❌ Error al procesar el archivo.");
      }
    } catch (error) {
      alert("❌ Error de conexión.");
    } finally {
      setGuardando(false);
    }
  };

  // 👇 Función Eliminar 👇
  const eliminarProducto = async (id: number) => {
    if (!confirm("¿Seguro que quieres borrar este producto de los estantes?")) return;
    
    try {
      const respuesta = await fetch(`http://localhost:8000/api/inventario/${id}`, {
        method: "DELETE",
      });
      if (respuesta.ok) {
        cargarInventario();
      }
    } catch (error) {
      alert("❌ Error eliminando producto.");
    }
  };

  // 👇 Funciones de Edición 👇
  const iniciarEdicion = (producto: any) => {
    setEditandoId(producto.id);
    setEditNombre(producto.nombre);
    setEditPrecio(producto.precio.toString());
    setEditCategoria(producto.categoria || '');
  };

  const guardarEdicion = async (id: number) => {
    try {
      const respuesta = await fetch(`http://localhost:8000/api/inventario/${id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ nombre: editNombre, precio: parseFloat(editPrecio), categoria: editCategoria }),
      });
      
      if (respuesta.ok) {
        setEditandoId(null);
        cargarInventario();
      }
    } catch (error) {
      alert("❌ Error al actualizar.");
    }
  };

  return (
    <div className="p-8 max-w-7xl mx-auto bg-gray-50 min-h-screen font-sans">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 tracking-tight">Gestión de Inventario</h1>
        <p className="text-gray-500 mt-2 text-sm">Carga masiva, individual y control total de tus estantes.</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* COLUMNA IZQUIERDA: Formularios (1/3) */}
        <div className="lg:col-span-1 space-y-4">
          <div className="flex bg-gray-200 p-1 rounded-xl">
            <button onClick={() => setModoCarga('manual')} className={`flex-1 py-2 rounded-lg text-sm font-medium transition-all ${modoCarga === 'manual' ? 'bg-white shadow text-blue-600' : 'text-gray-500'}`}>Manual</button>
            <button onClick={() => setModoCarga('csv')} className={`flex-1 py-2 rounded-lg text-sm font-medium transition-all ${modoCarga === 'csv' ? 'bg-white shadow text-blue-600' : 'text-gray-500'}`}>Importar CSV</button>
          </div>

          <div className="bg-white p-6 rounded-2xl border border-gray-200 shadow-sm">
            {modoCarga === 'manual' ? (
              <form onSubmit={agregarProducto} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Nombre</label>
                  <input type="text" value={nombre} onChange={(e) => setNombre(e.target.value)} className="w-full border border-gray-300 rounded-xl p-3 text-sm outline-none focus:border-blue-500" placeholder="Ej. Leche Entera" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Precio</label>
                  <input type="number" value={precio} onChange={(e) => setPrecio(e.target.value)} className="w-full border border-gray-300 rounded-xl p-3 text-sm outline-none focus:border-blue-500" placeholder="Ej. 4500" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Categoría</label>
                  <input type="text" value={categoria} onChange={(e) => setCategoria(e.target.value)} className="w-full border border-gray-300 rounded-xl p-3 text-sm outline-none focus:border-blue-500" placeholder="Opcional" />
                </div>
                <button type="submit" disabled={guardando} className="mt-4 w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-3 rounded-xl transition-all">
                  {guardando ? 'Guardando...' : 'Agregar Producto'}
                </button>
              </form>
            ) : (
              <form onSubmit={subirArchivoCSV} className="space-y-4 text-center">
                <div className="border-2 border-dashed border-gray-300 rounded-xl p-8 hover:bg-gray-50 transition-colors relative cursor-pointer">
                  <span className="text-3xl mb-2 block">📄</span>
                  <p className="text-sm font-medium text-gray-700 mb-1">Selecciona un archivo CSV</p>
                  <input type="file" accept=".csv" onChange={(e) => setArchivoCSV(e.target.files?.[0] || null)} className="absolute inset-0 w-full h-full opacity-0 cursor-pointer" />
                </div>
                {archivoCSV && <p className="text-xs text-green-600 font-semibold bg-green-50 p-2 rounded-lg">{archivoCSV.name}</p>}
                
                <button type="submit" disabled={guardando || !archivoCSV} className="w-full bg-blue-600 disabled:bg-gray-400 hover:bg-blue-700 text-white font-medium py-3 rounded-xl transition-all">
                  {guardando ? 'Procesando archivo...' : 'Subir Inventario Masivo'}
                </button>
              </form>
            )}
          </div>
        </div>

        {/* COLUMNA DERECHA: Tabla con Acciones (2/3) */}
        <div className="lg:col-span-2">
          <div className="bg-white p-6 rounded-2xl border border-gray-200 shadow-sm min-h-full">
            <h2 className="text-xl font-semibold text-gray-800 mb-6">Tus Productos Activos ({productos.length})</h2>
            
            {cargando ? (
              <p className="text-gray-500 text-center py-10">Cargando...</p>
            ) : (
              <div className="overflow-x-auto rounded-xl border border-gray-200">
                <table className="w-full text-sm text-left text-gray-500">
                  <thead className="text-xs text-gray-700 uppercase bg-gray-50 border-b">
                    <tr>
                      <th className="px-4 py-3">Producto</th>
                      <th className="px-4 py-3">Categoría</th>
                      <th className="px-4 py-3 text-right">Precio</th>
                      <th className="px-4 py-3 text-center">Acciones</th>
                    </tr>
                  </thead>
                  <tbody>
                    {productos.map((producto, idx) => (
                      <tr key={idx} className="bg-white border-b hover:bg-gray-50">
                        {/* MODO EDICIÓN */}
                        {editandoId === producto.id ? (
                          <>
                            <td className="px-4 py-2"><input type="text" value={editNombre} onChange={(e)=>setEditNombre(e.target.value)} className="w-full border rounded p-1 text-sm"/></td>
                            <td className="px-4 py-2"><input type="text" value={editCategoria} onChange={(e)=>setEditCategoria(e.target.value)} className="w-full border rounded p-1 text-sm"/></td>
                            <td className="px-4 py-2"><input type="number" value={editPrecio} onChange={(e)=>setEditPrecio(e.target.value)} className="w-full border rounded p-1 text-sm text-right"/></td>
                            <td className="px-4 py-2 text-center space-x-2">
                              <button onClick={() => guardarEdicion(producto.id)} className="text-green-600 hover:text-green-800" title="Guardar">💾</button>
                              <button onClick={() => setEditandoId(null)} className="text-gray-400 hover:text-gray-600" title="Cancelar">❌</button>
                            </td>
                          </>
                        ) : (
                          /* MODO VISTA NORMAL */
                          <>
                            <td className="px-4 py-3 font-medium text-gray-900">{producto.nombre}</td>
                            <td className="px-4 py-3">{producto.categoria}</td>
                            <td className="px-4 py-3 text-right">${producto.precio.toLocaleString("es-CO")}</td>
                            <td className="px-4 py-3 text-center space-x-3">
                              <button onClick={() => iniciarEdicion(producto)} className="text-blue-500 hover:text-blue-700 transition" title="Editar">✏️</button>
                              <button onClick={() => eliminarProducto(producto.id)} className="text-red-500 hover:text-red-700 transition" title="Eliminar">🗑️</button>
                            </td>
                          </>
                        )}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>

      </div>
    </div>
  );
}