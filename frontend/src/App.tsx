import { useState, useEffect, useRef } from 'react'
import { onAuthStateChanged, signOut } from 'firebase/auth'
import type { User } from 'firebase/auth'
import { Upload, RotateCcw, Menu, UserCircle, Settings, LogOut } from 'lucide-react'
import logoImg from './assets/logo.png'
import ResultCard from './components/ResultCard'
import BreakdownTable from './components/BreakdownTable'
import AuthModal from './components/AuthModal'
import Sidebar from './components/Sidebar'
import HistoryPage from './components/HistoryPage'
import AnalysisDetail from './components/AnalysisDetail'
import CollectionsPage from './components/CollectionsPage'
import LevelsPage from './components/LevelsPage'
import SettingsModal from './components/SettingsModal'
import { analyzeVideo, saveAnalysis, getUserProfile } from './api/client'
import type { AnalysisResult, SavedAnalysis, UserProfile } from './api/client'
import { auth } from './firebase'

// ── Texto animado ────────────────────────────────────────
const PHRASE = 'Only practice and constancy makes your Serve Better.'

interface VideoCanvasProps {
  src: string
  canvasFilter?: string
  opacity?: number
}

function VideoCanvas({ src, canvasFilter, opacity = 0.45 }: VideoCanvasProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const videoRef  = useRef<HTMLVideoElement>(null)

  useEffect(() => {
    const video  = videoRef.current
    const canvas = canvasRef.current
    if (!video || !canvas) return
    const ctx = canvas.getContext('2d')
    if (!ctx) return

    let animId: number
    const draw = () => {
      if (video.readyState >= 2) ctx.drawImage(video, 0, 0, canvas.width, canvas.height)
      animId = requestAnimationFrame(draw)
    }
    video.play().catch(() => {})
    animId = requestAnimationFrame(draw)
    return () => cancelAnimationFrame(animId)
  }, [src])

  return (
    <>
      <video
        ref={videoRef}
        loop muted playsInline
        src={src}
        style={{ position: 'absolute', width: 0, height: 0, opacity: 0, pointerEvents: 'none' }}
      />
      <canvas
        ref={canvasRef}
        width={1920} height={1080}
        className="fixed inset-0 w-full h-full scale-110 pointer-events-none"
        style={{ filter: canvasFilter, opacity, objectFit: 'cover', zIndex: 0 }}
      />
    </>
  )
}

function TypewriterText() {
  const [displayed, setDisplayed] = useState('')
  const [deleting, setDeleting]   = useState(false)

  useEffect(() => {
    const speed = deleting ? 40 : 80
    const timeout = setTimeout(() => {
      if (!deleting && displayed.length < PHRASE.length) {
        setDisplayed(PHRASE.slice(0, displayed.length + 1))
      } else if (!deleting && displayed.length === PHRASE.length) {
        setTimeout(() => setDeleting(true), 2500)
      } else if (deleting && displayed.length > 0) {
        setDisplayed(PHRASE.slice(0, displayed.length - 1))
      } else {
        setDeleting(false)
      }
    }, speed)
    return () => clearTimeout(timeout)
  }, [displayed, deleting])

  return (
    <div className="relative flex items-center justify-center h-[calc(100vh-80px)] overflow-hidden">
      <VideoCanvas src="/bg-serve.mp4" canvasFilter="blur(4px) brightness(0.38) hue-rotate(280deg) saturate(2.2)" opacity={0.5} />
      <div className="fixed inset-0 bg-gradient-to-b from-[#0d1117] via-transparent to-[#0d1117] pointer-events-none" style={{ zIndex: 1 }} />
      <p className="relative text-2xl sm:text-4xl font-bold text-center max-w-2xl mx-auto px-6 leading-relaxed" style={{ zIndex: 2 }}>
        <span className="bg-gradient-to-r from-[#c084fc] via-white to-[#818cf8] bg-clip-text text-transparent">
          {displayed}
        </span>
        <span className="animate-pulse text-[#e879f9]">|</span>
      </p>
      <p className="absolute bottom-4 left-1/2 -translate-x-1/2 text-xs italic whitespace-nowrap text-slate-600" style={{ zIndex: 2 }}>
        Trabajo de Fin de Grado — David Salas Merino
      </p>
    </div>
  )
}

// ── App ──────────────────────────────────────────────────
type View = 'home' | 'history' | 'detail' | 'collections' | 'levels'

function App() {
  const [user, setUser]               = useState<User | null>(null)
  const [authLoading, setAuthLoading] = useState(true)
  const isDarkMode = true
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [result, setResult]           = useState<AnalysisResult | null>(null)
  const [error, setError]             = useState<string | null>(null)
  const [authModal, setAuthModal]     = useState<'login' | 'register' | null>(null)
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [settingsOpen, setSettingsOpen] = useState(false)
  const [profileMenuOpen, setProfileMenuOpen] = useState(false)
  const [view, setView]               = useState<View>('home')
  const [selectedAnalysis, setSelectedAnalysis] = useState<SavedAnalysis | null>(null)
  const [previousView, setPreviousView]         = useState<View>('history')
  const [profile, setProfile]                   = useState<UserProfile | null>(null)

  const profileMenuRef = useRef<HTMLDivElement>(null)
  const accentColor    = '#7c3aed'

  useEffect(() => {
    const unsub = onAuthStateChanged(auth, (u) => {
      setUser(u)
      setAuthLoading(false)
      if (u) {
        setAuthModal(null)
        getUserProfile(u.uid).then(setProfile)
      } else {
        setProfile(null)
      }
    })
    return unsub
  }, [])

  const isRestricted = profile &&
    (profile.sexo === 'Mujer' || profile.mano_dominante === 'Izquierda')

  // Cierra el menú de perfil si se hace clic fuera
  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (profileMenuRef.current && !profileMenuRef.current.contains(e.target as Node)) {
        setProfileMenuOpen(false)
      }
    }
    document.addEventListener('mousedown', handler)
    return () => document.removeEventListener('mousedown', handler)
  }, [])

  const themeClasses = isDarkMode
    ? 'bg-gradient-to-br from-[#080414] via-[#0d0520] to-[#080414] text-slate-50'
    : 'bg-gradient-to-br from-amber-50 via-stone-50 to-amber-100 text-stone-900'

  const headerClasses = isDarkMode
    ? 'bg-[#080414]/85 border-[#3b0764]/60'
    : 'bg-amber-50/90 border-stone-200/70'

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return
    setIsAnalyzing(true); setError(null); setResult(null)
    try {
      const nivel = profile?.nivel ?? 5
      const data = await analyzeVideo(file, nivel)
      setResult(data)
      if (user) {
        saveAnalysis(user.uid, file.name, data).catch(() => {})
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Error al analizar el vídeo.')
    } finally {
      setIsAnalyzing(false)
    }
  }

  const handleReset = () => {
    setResult(null); setError(null)
  }

  const handleGoHome = () => {
    setView('home'); handleReset()
  }

  const handleLogout = () => {
    signOut(auth); setView('home'); handleReset()
    setProfileMenuOpen(false)
  }

  const handleSelectAnalysis = (analysis: SavedAnalysis, from: View = 'history') => {
    setSelectedAnalysis(analysis)
    setPreviousView(from)
    setView('detail')
  }

  if (authLoading) return null

  return (
    <div className={`h-screen overflow-y-auto lg:overflow-hidden flex flex-col ${themeClasses}`}>

      {/* Fondo video — solo cuando está logueado */}
      {user && (
        <>
          <VideoCanvas
            src="/bg-logged.mp4"
            canvasFilter="blur(5px) brightness(0.22) saturate(1.4)"
            opacity={0.6}
          />
        </>
      )}

      {/* Modales */}
      {authModal && <AuthModal initialTab={authModal} onClose={() => setAuthModal(null)} />}
      {settingsOpen && user && (
        <SettingsModal
          uid={user.uid}
          onClose={() => setSettingsOpen(false)}
          onSave={() => getUserProfile(user.uid).then(setProfile)}
        />
      )}

      {/* Sidebar */}
      {user && (
        <Sidebar
          isOpen={sidebarOpen}
          onClose={() => setSidebarOpen(false)}
          currentView={view === 'detail' ? 'history' : view as 'home' | 'history' | 'collections' | 'levels'}
          onNavigate={(v) => { setView(v); setSelectedAnalysis(null) }}
          isDarkMode={isDarkMode}
        />
      )}

      {/* Header */}
      <header className={`${headerClasses} backdrop-blur-md border-b sticky top-0 z-40`}>
        <div className="w-full px-6 py-5">
          <div className="flex items-center justify-between">

            {/* Izquierda */}
            <div className="flex items-center space-x-4">
              {user && (
                <button onClick={() => setSidebarOpen(true)}
                  className="p-2 rounded-lg transition-colors hover:bg-[#3b0764]/40 text-[#e9d5ff]">
                  <Menu className="w-6 h-6" />
                </button>
              )}
              {/* Logo → vuelve al inicio */}
              <button onClick={handleGoHome} className="flex items-center space-x-3 hover:opacity-80 transition-opacity">
                <img src={logoImg} alt="BioServe logo" className="w-9 h-9 object-contain" style={{ filter: 'hue-rotate(160deg) saturate(1.5) brightness(1.1)' }} />
                <h1 className="text-3xl font-bold tracking-tight bg-gradient-to-r from-[#c084fc] via-[#e879f9] to-[#818cf8] bg-clip-text text-transparent">BioServe</h1>
              </button>
            </div>

            {/* Derecha */}
            <div className="flex items-center space-x-3">
              {!user ? (
                <>
                  <button onClick={() => setAuthModal('register')}
                    className="px-5 py-2.5 rounded-lg font-medium text-base transition-all hover:opacity-90 text-[#c084fc] border border-[#7c3aed]/70 hover:border-[#c084fc] bg-transparent">
                    Crear cuenta
                  </button>
                  <button onClick={() => setAuthModal('login')}
                    className="px-5 py-2.5 rounded-lg font-medium text-base text-white transition-all hover:opacity-90"
                    style={{ background: 'linear-gradient(135deg, #7c3aed, #c026d3)' }}>
                    Iniciar sesión
                  </button>
                </>
              ) : (
                <>
                  {result && view === 'home' && (
                    <button onClick={handleReset}
                      className={`hidden sm:flex items-center space-x-2 px-4 py-2 rounded-lg font-medium transition-all ${isDarkMode ? 'bg-slate-800 hover:bg-slate-700' : 'bg-slate-200 hover:bg-slate-300'}`}>
                      <RotateCcw className="w-4 h-4" />
                      <span>Nuevo Análisis</span>
                    </button>
                  )}

                  {/* Menú de perfil */}
                  <div className="relative" ref={profileMenuRef}>
                    <button
                      onClick={() => setProfileMenuOpen(o => !o)}
                      className="flex items-center gap-2 pl-3 pr-2 py-1.5 rounded-lg transition-colors bg-[#1a0a35] hover:bg-[#3b0764]/50 text-[#e9d5ff] border border-[#3b0764]/40">
                      {profile?.nombre && (
                        <span className="text-sm font-medium text-[#c084fc] max-w-[120px] truncate">{profile.nombre}</span>
                      )}
                      <UserCircle className="w-5 h-5 shrink-0" />
                    </button>

                    {profileMenuOpen && (
                      <div className="absolute right-0 mt-2 w-52 rounded-xl shadow-2xl shadow-[#7c3aed]/20 z-50 overflow-hidden border border-[#3b0764]/60 bg-[#0d0520]">
                        {profile?.nombre && (
                          <div className="px-4 py-3 border-b border-[#3b0764]/40">
                            <p className="text-xs text-[#c084fc]/60 font-medium">Conectado como</p>
                            <p className="text-sm text-white font-semibold truncate">{profile.nombre}</p>
                          </div>
                        )}
                        <button
                          onClick={() => { setSettingsOpen(true); setProfileMenuOpen(false) }}
                          className="w-full flex items-center space-x-3 px-4 py-3 text-sm font-medium text-[#e9d5ff] hover:bg-[#3b0764]/30 transition-colors">
                          <Settings className="w-4 h-4" />
                          <span>Configuración</span>
                        </button>
                        <button
                          onClick={handleLogout}
                          className="w-full flex items-center space-x-3 px-4 py-3 text-sm font-medium text-red-400 hover:bg-red-500/10 transition-colors border-t border-[#3b0764]/40">
                          <LogOut className="w-4 h-4" />
                          <span>Cerrar sesión</span>
                        </button>
                      </div>
                    )}
                  </div>
                </>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* Main */}
      <main className={`flex-1 overflow-y-auto px-4 sm:px-6 ${!user ? 'p-0' : (view === 'home' && !result) ? '' : 'py-8'}`}>

        {!user && <TypewriterText />}

        {user && view === 'history' && (
          <HistoryPage uid={user.uid} isDarkMode={isDarkMode} onSelect={handleSelectAnalysis} />
        )}

        {user && view === 'collections' && (
          <CollectionsPage uid={user.uid} onSelectAnalysis={(a) => handleSelectAnalysis(a, 'collections')} />
        )}

        {user && view === 'levels' && (
          <LevelsPage userNivel={profile?.nivel} />
        )}

        {user && view === 'detail' && selectedAnalysis && (
          <AnalysisDetail
            analysis={selectedAnalysis}
            isDarkMode={isDarkMode}
            onBack={() => setView(previousView)}
            backLabel={previousView === 'collections' ? 'Volver a la colección' : 'Volver al historial'}
          />
        )}

        {user && view === 'home' && isRestricted && (
          <div className="flex items-center justify-center min-h-[calc(100vh-180px)]">
            <div className="text-center max-w-lg mx-auto px-6">
              <div className="text-6xl mb-6">🎾</div>
              <h2 className="text-2xl font-bold mb-4">Lo sentimos</h2>
              <p className={`text-lg leading-relaxed ${isDarkMode ? 'text-slate-400' : 'text-slate-600'}`}>
                En estas primeras versiones el modelo no está capacitado para analizar a usuarios zurdos
                o jugadoras femeninas. La siguiente versión tiene como objetivo solventar este inconveniente.
              </p>
            </div>
          </div>
        )}

        {user && view === 'home' && !isRestricted && (
          <>
            {isAnalyzing && (
              <div className="relative flex items-center justify-center min-h-[calc(100vh-80px)]">
                <div className="text-center -mt-16">
                  <div className="inline-flex items-center justify-center w-48 h-48 mb-10 rounded-full animate-pulse"
                    style={{ backgroundColor: `${accentColor}20`, border: `3px solid ${accentColor}` }}>
                    <img src={logoImg} alt="logo" className="w-36 h-36 object-contain" style={{ filter: 'hue-rotate(160deg) saturate(1.5) brightness(1.1)' }} />
                  </div>
                  <h2 className="text-7xl font-black mb-4 bg-gradient-to-r from-[#c084fc] via-white to-[#818cf8] bg-clip-text text-transparent"
                    style={{ filter: 'drop-shadow(0 0 32px rgba(192,132,252,0.8))' }}>
                    Analizando tu saque...
                  </h2>
                  <p className="text-white font-medium text-2xl">
                    MediaPipe está procesando el vídeo frame a frame
                  </p>
                </div>
                <p className="absolute bottom-6 left-1/2 -translate-x-1/2 text-xs italic text-slate-500 whitespace-nowrap">
                  Trabajo realizado por — David Salas Merino
                </p>
              </div>
            )}

            {!isAnalyzing && error && (
              <div className="flex items-center justify-center min-h-[calc(100vh-180px)]">
                <div className="text-center">
                  <p className="text-red-400 text-lg mb-6">{error}</p>
                  <button onClick={handleReset} className="px-6 py-3 rounded-lg font-medium text-white"
                    style={{ backgroundColor: accentColor }}>
                    Intentar de nuevo
                  </button>
                </div>
              </div>
            )}

            {!isAnalyzing && !result && !error && (
              <div className="relative flex flex-col lg:flex-row lg:items-center lg:justify-center min-h-[calc(100vh-80px)] gap-8 py-10 lg:py-0 lg:-mt-20 lg:pr-16">

                  {/* ── Hero — centrado ── */}
                  <div className="flex flex-col items-center text-center w-full">
                    <div className="inline-flex items-center justify-center w-36 h-36 mb-8 rounded-full"
                      style={{ backgroundColor: `${accentColor}15`, border: `2px solid ${accentColor}` }}>
                      <img src={logoImg} alt="logo" className="w-28 h-28 object-contain" style={{ filter: 'hue-rotate(160deg) saturate(1.5) brightness(1.1)' }} />
                    </div>
                    <h2 className="text-5xl lg:text-7xl font-black mb-4 tracking-tight bg-gradient-to-r from-[#c084fc] via-white to-[#818cf8] bg-clip-text text-transparent"
                      style={{ filter: 'drop-shadow(0 0 28px rgba(192,132,252,0.8))' }}>
                      Analiza tu Saque
                    </h2>
                    <p className="mb-10 max-w-sm text-lg text-white font-medium">
                      Obtén análisis detallado de tu técnica de tenis con inteligencia artificial
                    </p>
                    <label style={{ background: 'linear-gradient(135deg, #7c3aed, #c026d3)' }}
                      className="inline-flex items-center space-x-3 px-8 py-4 text-white font-bold text-lg rounded-lg cursor-pointer transition-all hover:opacity-90 hover:scale-105 shadow-lg shadow-[#7c3aed]/30">
                      <Upload className="w-5 h-5" />
                      <span>Subir Vídeo</span>
                      <input type="file" accept="video/*" onChange={handleFileUpload} className="hidden" />
                    </label>
                  </div>

                  {/* ── Tips — derecha en desktop, abajo en móvil ── */}
                  <div className="rounded-2xl border bg-[#0d0520]/80 border-[#3b0764]/60 backdrop-blur-sm p-6 w-full lg:shrink-0 lg:mt-32" style={{ maxWidth: '420px', margin: '0 auto' }}>
                    <h3 className="text-base font-black mb-5 bg-gradient-to-r from-[#c084fc] via-white to-[#818cf8] bg-clip-text text-transparent"
                      style={{ filter: 'drop-shadow(0 0 10px rgba(192,132,252,0.4))' }}>
                      Sugerencias para mejores Resultados
                    </h3>
                    <ul className="space-y-3 mb-5">
                      {[
                        'Grábate desde una altura media (aprox. a la altura del pecho)',
                        'Coloca la cámara detrás del jugador, con perspectiva desde la derecha',
                        'Cuanta mayor iluminación tengas, mejor será el análisis',
                      ].map(text => (
                        <li key={text} className="flex items-start gap-3">
                          <span className="mt-1.5 w-1.5 h-1.5 rounded-full bg-[#c084fc] shrink-0" />
                          <p className="text-[#e9d5ff]/90 text-sm leading-relaxed">{text}</p>
                        </li>
                      ))}
                    </ul>
                    <p className="text-xs text-[#c084fc]/60 mb-2 font-medium">Ejemplo de ángulo</p>
                    <img
                      src="/example-angle.png"
                      alt="Ángulo correcto de grabación"
                      className="rounded-xl border border-[#3b0764]/50 block mx-auto"
                      style={{ maxHeight: '260px', maxWidth: '100%', objectFit: 'contain', display: 'block' }}
                    />
                  </div>

              </div>
            )}

            {!isAnalyzing && result && (
              <>
                <div className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-3 gap-6">
                  <div className="lg:col-span-2">
                    <ResultCard result={result} isDarkMode={isDarkMode} accentColor={accentColor} />
                  </div>
                  <div className="lg:col-span-1">
                    <BreakdownTable breakdown={result.breakdown} isDarkMode={isDarkMode} />
                  </div>
                </div>

              </>
            )}
          </>
        )}
      </main>

    </div>
  )
}

export default App
