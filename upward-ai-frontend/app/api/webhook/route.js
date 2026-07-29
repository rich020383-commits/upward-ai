import { NextResponse } from 'next/server';
import { GoogleGenerativeAI } from '@google/generative-ai';

// 1. Inicializamos Gemini con tu clave de entorno
const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY);
const model = genAI.getGenerativeModel({ model: "gemini-1.5-flash" }); 

// La contraseña definitiva para Meta
const MI_TOKEN_SECRETO = "upway_business_secreto_2026";

// ==========================================
// GET: META USA ESTO PARA VERIFICAR EL ENLACE
// ==========================================
export async function GET(request) {
  const { searchParams } = new URL(request.url);
  const mode = searchParams.get("hub.mode");
  const token = searchParams.get("hub.verify_token");
  const challenge = searchParams.get("hub.challenge");

  if (mode === "subscribe" && token === MI_TOKEN_SECRETO) {
    console.log("¡Webhook de Upway Business conectado a Meta! ✅");
    return new NextResponse(challenge, { status: 200 });
  }
  
  return NextResponse.json({ error: "Token inválido" }, { status: 403 });
}

// ==========================================
// POST: AQUÍ LLEGAN LOS MENSAJES Y RESPONDE GEMINI
// ==========================================
export async function POST(request) {
  try {
    const body = await request.json();

    if (body.object === "whatsapp_business_account") {
      const entry = body.entry?.[0];
      const changes = entry?.changes?.[0];
      const value = changes?.value;
      const messages = value?.messages;

      // Si hay un mensaje entrante
      if (messages && messages.length > 0) {
        const message = messages[0];
        const from = message.from; // Número de quien te escribe
        const text = message.text?.body; // El mensaje del cliente

        if (text) {
          console.log(`Mensaje recibido de ${from}: ${text}`);

          // A. Le pasamos el texto a Gemini
          const prompt = `Eres el gerente digital y asistente virtual exclusivo de Upway Business. Responde de forma amable, profesional y concisa a este cliente: "${text}"`;
          const result = await model.generateContent(prompt);
          const geminiResponse = result.response.text();

          // B. Enviamos la respuesta de vuelta por WhatsApp
          const whatsappUrl = `https://graph.facebook.com/v19.0/${value.metadata.phone_number_id}/messages`;
          
          await fetch(whatsappUrl, {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${process.env.WHATSAPP_TOKEN}`,
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              messaging_product: "whatsapp",
              to: from,
              text: { body: geminiResponse },
            }),
          });
        }
      }
      return NextResponse.json({ status: "ok" }, { status: 200 });
    }
    
    return NextResponse.json({ error: "Evento ignorado" }, { status: 404 });
  } catch (error) {
    console.error("Error procesando mensaje:", error);
    return NextResponse.json({ error: "Error interno" }, { status: 500 });
  }
}