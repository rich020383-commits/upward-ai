export default function Footer() {
  return (
    <footer className="bg-slate-950 text-slate-400 py-16">
      <div className="max-w-7xl mx-auto px-6 grid grid-cols-1 md:grid-cols-4 gap-12">
        <div className="space-y-4">
          <div className="text-white font-bold text-xl tracking-tight">UPWARD AI</div>
          <p className="text-sm">Potenciando empresas mediante Inteligencia Artificial estratégica.</p>
        </div>
        
        <div>
          <h4 className="text-white font-semibold mb-6">Soluciones</h4>
          <ul className="space-y-3 text-sm">
            <li>Automatización RPA</li>
            <li>Agentes IA</li>
            <li>Consultoría</li>
          </ul>
        </div>

        <div>
          <h4 className="text-white font-semibold mb-6">Empresa</h4>
          <ul className="space-y-3 text-sm">
            <li>Nosotros</li>
            <li>Casos de Éxito</li>
            <li>Contacto</li>
          </ul>
        </div>

        <div>
          <h4 className="text-white font-semibold mb-6">Legal</h4>
          <ul className="space-y-3 text-sm">
            <li>Privacidad</li>
            <li>Términos de servicio</li>
          </ul>
        </div>
      </div>
      <div className="max-w-7xl mx-auto px-6 mt-16 pt-8 border-t border-slate-800 text-sm text-center md:text-left">
        © {new Date().getFullYear()} Upward AI. Todos los derechos reservados.
      </div>
    </footer>
  );
}