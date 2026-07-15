import { useState } from 'react'
import { X } from 'lucide-react'
import { createUserWithEmailAndPassword, signInWithEmailAndPassword, sendPasswordResetEmail } from 'firebase/auth'
import { doc, setDoc } from 'firebase/firestore'
import { auth, db } from '../firebase'

type Tab = 'login' | 'register' | 'forgot'

interface Props {
  initialTab: 'login' | 'register'
  onClose:    () => void
}

export default function AuthModal({ initialTab, onClose }: Props) {
  const [tab, setTab]         = useState<Tab>(initialTab)
  const [loading, setLoading] = useState(false)
  const [error, setError]     = useState('')
  const [info, setInfo]       = useState('')

  const [email, setEmail]       = useState('')
  const [password, setPassword] = useState('')
  const [nombre, setNombre]             = useState('')
  const [altura, setAltura]             = useState('')
  const [sexo, setSexo]                 = useState('Hombre')
  const [manoDominante, setManoDominante] = useState('Derecha')
  const [nivel, setNivel]               = useState(1)

  const LEVEL_LABELS: Record<number, string> = {
    1: 'Iniciación', 2: 'Básico', 3: 'Intermedio', 4: 'Avanzado', 5: 'Competición',
  }

  const resetMessages = () => { setError(''); setInfo('') }

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true); resetMessages()
    try {
      await signInWithEmailAndPassword(auth, email, password)
    } catch {
      setError('Correo o contraseña incorrectos.')
    } finally {
      setLoading(false)
    }
  }

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault()
    resetMessages()
    const alturaNum = Number(altura)
    if (!altura || alturaNum < 100 || alturaNum > 230) {
      setError('Introduce una altura válida entre 100 y 230 cm.')
      return
    }
    setLoading(true)
    try {
      const { user } = await createUserWithEmailAndPassword(auth, email, password)
      await setDoc(doc(db, 'users', user.uid), {
        nombre,
        email,
        altura:         alturaNum,
        sexo,
        mano_dominante: manoDominante,
        nivel,
        created_at:     new Date().toISOString(),
      })
    } catch (err: any) {
      if (err.code === 'auth/email-already-in-use') {
        setError('Ese correo ya está registrado.')
      } else if (err.code === 'auth/weak-password') {
        setError('La contraseña debe tener al menos 6 caracteres.')
      } else {
        setError('Error al crear la cuenta. Inténtalo de nuevo.')
      }
    } finally {
      setLoading(false)
    }
  }

  const handleForgot = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true); resetMessages()
    try {
      await sendPasswordResetEmail(auth, email)
      setInfo('Correo de recuperación enviado. Revisa tu bandeja de entrada.')
    } catch {
      setError('No existe ninguna cuenta con ese correo.')
    } finally {
      setLoading(false)
    }
  }

  const inputClass = 'w-full px-4 py-3 rounded-lg bg-[#12082a] border border-[#3b0764]/60 text-slate-100 placeholder-slate-500 focus:outline-none focus:border-[#c084fc] text-base transition-colors'
  const labelClass = 'block text-sm font-medium text-[#c084fc]/70 mb-1.5'

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm">

      <div className="bg-[#0d0520] border border-[#3b0764]/70 rounded-2xl p-10 w-full max-w-xl shadow-2xl shadow-[#7c3aed]/10 mx-4 relative">

        <button
          onClick={onClose}
          className="absolute top-4 right-4 p-1.5 rounded-lg text-[#c084fc]/50 hover:text-[#c084fc] hover:bg-[#3b0764]/40 transition-colors"
        >
          <X className="w-5 h-5" />
        </button>

        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold bg-gradient-to-r from-[#c084fc] via-[#e879f9] to-[#818cf8] bg-clip-text text-transparent">ServeAnalyzer</h1>
          <p className="text-slate-500 text-base mt-1.5">Análisis biomecánico de saques</p>
        </div>

        {tab !== 'forgot' && (
          <div className="flex rounded-lg bg-[#12082a] p-1 mb-7 border border-[#3b0764]/40">
            <button
              onClick={() => { setTab('login'); resetMessages() }}
              className={`flex-1 py-2.5 rounded-md text-base font-medium transition-all ${
                tab === 'login'
                  ? 'text-white'
                  : 'text-slate-500 hover:text-[#c084fc]'
              }`}
              style={tab === 'login' ? { background: 'linear-gradient(135deg, #7c3aed, #c026d3)' } : {}}
            >
              Iniciar sesión
            </button>
            <button
              onClick={() => { setTab('register'); resetMessages() }}
              className={`flex-1 py-2.5 rounded-md text-base font-medium transition-all ${
                tab === 'register'
                  ? 'text-white'
                  : 'text-slate-500 hover:text-[#c084fc]'
              }`}
              style={tab === 'register' ? { background: 'linear-gradient(135deg, #7c3aed, #c026d3)' } : {}}
            >
              Crear cuenta
            </button>
          </div>
        )}

        {tab === 'login' && (
          <form onSubmit={handleLogin} className="space-y-5">
            <div>
              <label className={labelClass}>Correo electrónico</label>
              <input type="email" required placeholder="tu@correo.com" value={email} onChange={e => setEmail(e.target.value)} className={inputClass} />
            </div>
            <div>
              <label className={labelClass}>Contraseña</label>
              <input type="password" required placeholder="••••••••" value={password} onChange={e => setPassword(e.target.value)} className={inputClass} />
            </div>
            <button
              type="button"
              onClick={() => { setTab('forgot'); resetMessages() }}
              className="text-xs text-[#c084fc]/60 hover:text-[#c084fc] transition-colors"
            >
              ¿Olvidaste tu contraseña?
            </button>
            {error && <p className="text-red-400 text-sm">{error}</p>}
            <button type="submit" disabled={loading}
              className="w-full py-3 rounded-lg text-white font-semibold text-base transition-all hover:opacity-90 disabled:opacity-50"
              style={{ background: 'linear-gradient(135deg, #7c3aed, #c026d3)' }}>
              {loading ? 'Entrando...' : 'Iniciar sesión'}
            </button>
          </form>
        )}

        {tab === 'register' && (
          <form onSubmit={handleRegister} className="space-y-5">
            <div>
              <label className={labelClass}>Nombre</label>
              <input type="text" required placeholder="Tu nombre" value={nombre} onChange={e => setNombre(e.target.value)} className={inputClass} />
            </div>
            <div>
              <label className={labelClass}>Correo electrónico</label>
              <input type="email" required placeholder="tu@correo.com" value={email} onChange={e => setEmail(e.target.value)} className={inputClass} />
            </div>
            <div>
              <div className="flex items-center gap-1.5 mb-1">
                <label className={labelClass} style={{ marginBottom: 0 }}>Contraseña</label>
                <div className="relative group">
                  <span className="flex items-center justify-center w-4 h-4 rounded-full border border-[#c084fc]/50 text-[#c084fc]/70 text-[10px] font-bold cursor-default select-none hover:border-[#c084fc] hover:text-[#c084fc] transition-colors">!</span>
                  <div className="absolute left-1/2 -translate-x-1/2 bottom-full mb-2 w-56 bg-[#1a0a35] border border-[#3b0764] rounded-lg px-3 py-2.5 text-xs text-slate-300 shadow-lg shadow-black/50 invisible group-hover:visible opacity-0 group-hover:opacity-100 transition-all duration-150 z-10 pointer-events-none">
                    <p className="font-semibold text-[#c084fc] mb-1.5">Requisitos de contraseña</p>
                    <ul className="space-y-1 text-slate-400">
                      <li>• Entre 8 y 16 caracteres</li>
                      <li>• Al menos 1 letra mayúscula</li>
                      <li>• Al menos 1 número</li>
                      <li>• Al menos 1 símbolo especial (!@#$%...)</li>
                    </ul>
                    <div className="absolute left-1/2 -translate-x-1/2 top-full w-2 h-2 bg-[#1a0a35] border-r border-b border-[#3b0764] rotate-45 -mt-1" />
                  </div>
                </div>
              </div>
              <input type="password" required placeholder="Mínimo 8 caracteres" value={password} onChange={e => setPassword(e.target.value)} className={inputClass} />
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className={labelClass}>Altura (cm)</label>
                <input type="number" required min={100} max={230} placeholder="175" value={altura} onChange={e => setAltura(e.target.value)} className={inputClass} />
              </div>
              <div>
                <label className={labelClass}>Mano dominante</label>
                <select value={manoDominante} onChange={e => setManoDominante(e.target.value)} className={inputClass}>
                  <option>Derecha</option>
                  <option>Izquierda</option>
                </select>
              </div>
            </div>
            <div>
              <label className={labelClass}>Sexo</label>
              <select value={sexo} onChange={e => setSexo(e.target.value)} className={inputClass}>
                <option>Hombre</option>
                <option>Mujer</option>
                <option>Prefiero no decirlo</option>
              </select>
            </div>
            <div>
              <label className={labelClass}>Nivel de juego</label>
              <div className="flex gap-1.5">
                {[1,2,3,4,5].map(n => (
                  <div key={n} className="flex-1 flex flex-col items-center gap-1">
                    <button type="button" onClick={() => setNivel(n)}
                      className="w-full py-2 rounded-lg text-sm font-bold transition-all"
                      style={nivel === n
                        ? { background: 'linear-gradient(135deg, #7c3aed, #c026d3)', color: '#fff' }
                        : { color: '#c084fc', border: '1px solid rgba(124,58,237,0.4)' }}>
                      {n}
                    </button>
                    <span className="text-[10px] text-[#c084fc]/50 text-center leading-tight">{LEVEL_LABELS[n]}</span>
                  </div>
                ))}
              </div>
            </div>

            {error && <p className="text-red-400 text-sm">{error}</p>}
            <button type="submit" disabled={loading}
              className="w-full py-3 rounded-lg text-white font-semibold text-base transition-all hover:opacity-90 disabled:opacity-50"
              style={{ background: 'linear-gradient(135deg, #7c3aed, #c026d3)' }}>
              {loading ? 'Creando cuenta...' : 'Crear cuenta'}
            </button>
          </form>
        )}

        {tab === 'forgot' && (
          <form onSubmit={handleForgot} className="space-y-5">
            <p className="text-slate-500 text-sm">Introduce tu correo y te enviaremos un enlace para restablecer la contraseña.</p>
            <div>
              <label className={labelClass}>Correo electrónico</label>
              <input type="email" required placeholder="tu@correo.com" value={email} onChange={e => setEmail(e.target.value)} className={inputClass} />
            </div>
            {error && <p className="text-red-400 text-sm">{error}</p>}
            {info  && <p className="text-[#c084fc] text-sm">{info}</p>}
            <button type="submit" disabled={loading}
              className="w-full py-3 rounded-lg text-white font-semibold text-base transition-all hover:opacity-90 disabled:opacity-50"
              style={{ background: 'linear-gradient(135deg, #7c3aed, #c026d3)' }}>
              {loading ? 'Enviando...' : 'Enviar enlace'}
            </button>
            <button type="button" onClick={() => { setTab('login'); resetMessages() }} className="w-full text-sm text-slate-500 hover:text-[#c084fc] transition-colors">
              ← Volver al inicio de sesión
            </button>
          </form>
        )}

      </div>
    </div>
  )
}
