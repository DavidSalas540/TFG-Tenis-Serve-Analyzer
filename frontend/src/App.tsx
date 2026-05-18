import { useState } from 'react'
import { Upload, RotateCcw, Sun, Moon, Menu, X } from 'lucide-react'
import { TennisBall } from './components/TennisBall'
import ResultCard from './components/ResultCard'
import BreakdownTable from './components/BreakdownTable'
import { analyzeVideo } from './api/client'
import type { AnalysisResult } from './api/client'

function App() {
  const [isDarkMode, setIsDarkMode] = useState(true)
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [result, setResult] = useState<AnalysisResult | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false)

  const accentColor = '#10b981'

  const themeClasses = isDarkMode
    ? 'bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 text-slate-50'
    : 'bg-gradient-to-br from-slate-50 via-white to-slate-100 text-slate-900'

  const headerClasses = isDarkMode
    ? 'bg-slate-900/80 border-slate-800/50'
    : 'bg-white/80 border-slate-200/50'

  // Cuando el usuario elige un fichero → llama a Flask
  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return

    setIsAnalyzing(true)
    setError(null)
    setResult(null)

    try {
      const data = await analyzeVideo(file)
      setResult(data)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Error al analizar el vídeo.')
    } finally {
      setIsAnalyzing(false)
    }
  }

  const handleReset = () => {
    setResult(null)
    setError(null)
  }

  return (
    <div className={`min-h-screen ${themeClasses}`}>

      {/* ── Header ── */}
      <header className={`${headerClasses} backdrop-blur-md border-b sticky top-0 z-50`}>
        <div className="w-full px-6 py-4">
          <div className="flex items-center justify-between">

            {/* Izquierda: menú + logo */}
            <div className="flex items-center space-x-4">
              <button
                onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
                className={`p-2 rounded-lg transition-colors ${isDarkMode ? 'hover:bg-slate-800' : 'hover:bg-slate-200'}`}
              >
                {isMobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
              </button>
              <div className="flex items-center space-x-3">
                <div style={{ color: accentColor }}>
                  <TennisBall className="w-8 h-8" />
                </div>
                <h1 className="text-2xl font-bold tracking-tight">BioServe</h1>
              </div>
            </div>

            {/* Derecha: botón reset + toggle tema */}
            <div className="flex items-center space-x-3">
              {result && (
                <button
                  onClick={handleReset}
                  className={`hidden sm:flex items-center space-x-2 px-4 py-2 rounded-lg font-medium transition-all ${isDarkMode ? 'bg-slate-800 hover:bg-slate-700' : 'bg-slate-200 hover:bg-slate-300'
                    }`}
                >
                  <RotateCcw className="w-4 h-4" />
                  <span>Nuevo Análisis</span>
                </button>
              )}
              <button
                onClick={() => setIsDarkMode(!isDarkMode)}
                className={`p-2 rounded-lg transition-colors ${isDarkMode ? 'bg-slate-800 hover:bg-slate-700' : 'bg-slate-200 hover:bg-slate-300'}`}
              >
                {isDarkMode ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* ── Main ── */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 py-8">

        {/* Pantalla de carga */}
        {isAnalyzing && (
          <div className="flex items-center justify-center min-h-[calc(100vh-180px)]">
            <div className="text-center">
              <div
                className="inline-flex items-center justify-center w-24 h-24 mb-6 rounded-full animate-pulse"
                style={{ backgroundColor: `${accentColor}20`, border: `2px solid ${accentColor}` }}
              >
                <div style={{ color: accentColor }}>
                  <TennisBall className="w-16 h-16" />
                </div>
              </div>
              <h2 className="text-2xl font-bold mb-2">Analizando tu saque...</h2>
              <p className={isDarkMode ? 'text-slate-400' : 'text-slate-600'}>
                MediaPipe está procesando el vídeo frame a frame
              </p>
            </div>
          </div>
        )}

        {/* Pantalla de error */}
        {!isAnalyzing && error && (
          <div className="flex items-center justify-center min-h-[calc(100vh-180px)]">
            <div className="text-center">
              <p className="text-red-400 text-lg mb-6">{error}</p>
              <button
                onClick={handleReset}
                className="px-6 py-3 rounded-lg font-medium text-white"
                style={{ backgroundColor: accentColor }}
              >
                Intentar de nuevo
              </button>
            </div>
          </div>
        )}

        {/* Pantalla de subida */}
        {!isAnalyzing && !result && !error && (
          <div className="flex items-center justify-center min-h-[calc(100vh-180px)]">
            <div className="text-center">
              <div
                className="inline-flex items-center justify-center w-32 h-32 mb-8 rounded-full"
                style={{ backgroundColor: `${accentColor}15`, border: `2px solid ${accentColor}` }}
              >
                <div style={{ color: accentColor }}>
                  <TennisBall className="w-24 h-24" />
                </div>
              </div>
              <h2 className="text-4xl font-bold mb-4 tracking-tight">Analiza tu Saque</h2>
              <p className={`mb-10 max-w-md mx-auto text-lg ${isDarkMode ? 'text-slate-400' : 'text-slate-600'}`}>
                Obtén análisis detallado de tu técnica de tenis con inteligencia artificial
              </p>
              <label
                style={{ backgroundColor: accentColor }}
                className="inline-flex items-center space-x-3 px-8 py-4 text-white font-semibold rounded-lg cursor-pointer transition-all hover:opacity-90 hover:scale-105 shadow-lg"
              >
                <Upload className="w-5 h-5" />
                <span>Subir Vídeo</span>
                <input
                  type="file"
                  accept="video/*"
                  onChange={handleFileUpload}
                  className="hidden"
                />
              </label>
            </div>
          </div>
        )}

        {/* Pantalla de resultados */}
        {!isAnalyzing && result && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2">
              <ResultCard result={result} isDarkMode={isDarkMode} accentColor={accentColor} />
            </div>
            <div className="lg:col-span-1">
              <BreakdownTable breakdown={result.breakdown} isDarkMode={isDarkMode} />
            </div>
          </div>
        )}

      </main>
    </div>
  )
}

export default App
