"use client";

import { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { MessageSquare, X, Send, Bot, Sparkles } from "lucide-react";

export default function Chatbot() {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([
    { role: "bot", content: "¡Hola! Soy el Agente Inteligente de Upward AI. ¿En qué proceso de tu empresa te gustaría implementar IA hoy?" }
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  
  // Referencia para hacer scroll automático hasta el último mensaje
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const sendMessage = async () => {
    if (!input.trim()) return;
    
    const userMessage = { role: "user", content: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    try {
      // Apuntamos dinámicamente al backend real en Render
      const baseUrl = process.env.NEXT_PUBLIC_API_URL || "https://upward-ai-8n4i.onrender.com";
      const res = await fetch(`${baseUrl}/api/chat/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: input }),
      });
      const data = await res.json();
      
      // Simulamos un pequeño retraso para que se vea el efecto de "Pensando..."
      setTimeout(() => {
        setMessages((prev) => [...prev, { role: "bot", content: data.reply }]);
        setIsLoading(false);
      }, 800);

    } catch (error) {
      setTimeout(() => {
        setMessages((prev) => [...prev, { role: "bot", content: "Lo siento, mis servidores están en mantenimiento. Por favor, intenta de nuevo en unos minutos." }]);
        setIsLoading(false);
      }, 800);
    }
  };

  return (
    <>
      {/* Botón flotante Premium */}
      <motion.button 
        initial={{ scale: 0 }}
        animate={{ scale: 1 }}
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
        onClick={() => setIsOpen(true)}
        className={`fixed bottom-6 right-6 p-4 rounded-full shadow-premium hover:shadow-2xl transition-all z-50 flex items-center justify-center ${
          isOpen ? 'bg-slate-900 text-white' : 'bg-blue-600 text-white'
        }`}
      >
        {isOpen ? <X className="w-6 h-6" /> : <MessageSquare className="w-6 h-6" />}
      </motion.button>

      {/* Ventana de chat Glassmorphism */}
      <AnimatePresence>
        {isOpen && (
          <motion.div 
            initial={{ opacity: 0, y: 20, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 20, scale: 0.95 }}
            transition={{ type: "spring", stiffness: 200, damping: 20 }}
            className="fixed bottom-24 right-6 w-[350px] md:w-[400px] h-[550px] bg-white/90 backdrop-blur-xl rounded-3xl shadow-2xl border border-slate-200 z-50 flex flex-col overflow-hidden"
          >
            {/* Header del Chat */}
            <div className="bg-slate-950 p-5 text-white flex items-center space-x-3 shrink-0">
              <div className="relative">
                <div className="w-10 h-10 bg-blue-600 rounded-full flex items-center justify-center">
                  <Bot className="w-6 h-6 text-white" />
                </div>
                <span className="absolute bottom-0 right-0 w-3 h-3 bg-green-500 border-2 border-slate-950 rounded-full"></span>
              </div>
              <div>
                <h3 className="font-bold text-sm tracking-wide flex items-center gap-1">
                  Upward AI <Sparkles className="w-3 h-3 text-blue-400" />
                </h3>
                <p className="text-xs text-slate-400">Agente Inteligente 24/7</p>
              </div>
            </div>
            
            {/* Área de mensajes */}
            <div className="flex-1 overflow-y-auto p-5 space-y-4 bg-slate-50/50 scroll-smooth">
              {messages.map((m, i) => (
                <motion.div 
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  key={i} 
                  className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div 
                    className={`max-w-[85%] p-4 text-sm leading-relaxed ${
                      m.role === 'user' 
                        ? 'bg-blue-600 text-white rounded-2xl rounded-tr-sm shadow-md' 
                        : 'bg-white text-slate-700 rounded-2xl rounded-tl-sm shadow-sm border border-slate-100'
                    }`}
                  >
                    {m.content}
                  </div>
                </motion.div>
              ))}
              
              {/* Animación de "Pensando..." */}
              {isLoading && (
                <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex justify-start">
                  <div className="bg-white p-4 rounded-2xl rounded-tl-sm shadow-sm border border-slate-100 flex items-center space-x-2">
                    <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                    <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                    <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                  </div>
                </motion.div>
              )}
              <div ref={messagesEndRef} />
            </div>

            {/* Input de texto */}
            <div className="p-4 bg-white border-t border-slate-100 shrink-0">
              <div className="relative flex items-center">
                <input 
                  value={input} 
                  onChange={(e) => setInput(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                  placeholder="Escribe tu consulta aquí..."
                  disabled={isLoading}
                  className="w-full bg-slate-50 border border-slate-200 focus:border-blue-500 focus:bg-white rounded-full pl-5 pr-12 py-3.5 text-sm text-slate-900 outline-none transition-all disabled:opacity-50"
                />
                <button 
                  onClick={sendMessage} 
                  disabled={isLoading || !input.trim()}
                  className="absolute right-2 top-1/2 -translate-y-1/2 bg-blue-600 hover:bg-blue-700 disabled:bg-slate-300 text-white p-2 rounded-full transition-colors flex items-center justify-center"
                >
                  <Send className="w-4 h-4" />
                </button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}