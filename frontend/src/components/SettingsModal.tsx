import { useState, useEffect } from 'react'
import { X } from 'lucide-react'
import { doc, getDoc, updateDoc } from 'firebase/firestore'
import { db } from '../firebase'

interface Props {
    uid:      string
    onClose:  () => void
    onSave:   () => void
}

export default function SettingsModal({ uid, onClose, onSave }: Props) {
    const [loading, setSaving]   = useState(false)
    const [fetching, setFetching] = useState(true)
    const [saved, setSaved]       = useState(false)
    const [error, setError]       = useState('')

    const [nombre, setNombre]               = useState('')
    const [altura, setAltura]               = useState('')
    const [sexo, setSexo]                   = useState('Hombre')
    const [manoDominante, setManoDominante] = useState('Derecha')
    const [nivel, setNivel]                 = useState(1)

    const LEVEL_LABELS: Record<number, string> = {
        1: 'Iniciación', 2: 'Básico', 3: 'Intermedio', 4: 'Avanzado', 5: 'Competición',
    }

    useEffect(() => {
        getDoc(doc(db, 'users', uid)).then(snap => {
            if (snap.exists()) {
                const d = snap.data()
                setNombre(d.nombre ?? '')
                setAltura(String(d.altura ?? ''))
                setSexo(d.sexo ?? 'Hombre')
                setManoDominante(d.mano_dominante ?? 'Derecha')
                setNivel(d.nivel ?? 1)
            }
        }).finally(() => setFetching(false))
    }, [uid])

    const handleSave = async (e: React.FormEvent) => {
        e.preventDefault()
        setSaving(true); setError(''); setSaved(false)
        try {
            await updateDoc(doc(db, 'users', uid), {
                nombre,
                altura:         Number(altura),
                sexo,
                mano_dominante: manoDominante,
                nivel,
            })
            setSaved(true)
            onSave()
            onClose()
        } catch {
            setError('Error al guardar. Inténtalo de nuevo.')
        } finally {
            setSaving(false)
        }
    }

    const inputClass = 'w-full px-4 py-3 rounded-lg bg-[#1a0f3a] border border-[#3b0764]/90 text-slate-100 placeholder-slate-500 focus:outline-none focus:border-[#c084fc] text-base transition-colors'
    const labelClass = 'block text-sm font-medium text-[#c084fc] mb-1.5'

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm">
            <div className="bg-[#150a30] border border-[#7c3aed]/60 rounded-2xl w-full max-w-2xl mx-4 shadow-2xl shadow-[#7c3aed]/20 relative">

                <div className="flex items-center justify-between px-8 py-6 border-b border-[#3b0764]/60">
                    <div>
                        <h2 className="text-xl font-bold bg-gradient-to-r from-[#c084fc] to-[#818cf8] bg-clip-text text-transparent">Configuración</h2>
                        <p className="text-slate-400 text-base">Edita los datos de tu perfil</p>
                    </div>
                    <button onClick={onClose} className="p-1.5 rounded-lg text-[#c084fc] hover:bg-[#3b0764]/40 transition-colors">
                        <X className="w-5 h-5" />
                    </button>
                </div>

                <form onSubmit={handleSave} className="px-8 py-7 space-y-5">
                    {fetching ? (
                        <p className="text-slate-500 text-center py-8">Cargando datos...</p>
                    ) : (
                        <>
                            <div>
                                <label className={labelClass}>Nombre</label>
                                <input type="text" value={nombre} onChange={e => setNombre(e.target.value)} className={inputClass} />
                            </div>

                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <label className={labelClass}>Altura (cm)</label>
                                    <input type="number" min={100} max={230} value={altura} onChange={e => setAltura(e.target.value)} className={inputClass} />
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
                                                    : { color: '#c084fc', border: '1px solid rgba(124,58,237,0.65)' }}>
                                                {n}
                                            </button>
                                            <span className="text-xs text-[#c084fc] text-center leading-tight">{LEVEL_LABELS[n]}</span>
                                        </div>
                                    ))}
                                </div>
                            </div>

                            {error && <p className="text-red-400 text-sm">{error}</p>}
                            {saved && <p className="text-[#c084fc] text-sm">✓ Cambios guardados correctamente</p>}

                            <div className="flex justify-end pt-2">
                                <button type="submit" disabled={loading}
                                    className="px-8 py-3 rounded-lg text-white font-semibold text-base transition-all hover:opacity-90 disabled:opacity-50"
                                    style={{ background: 'linear-gradient(135deg, #7c3aed, #c026d3)' }}>
                                    {loading ? 'Guardando...' : 'Guardar cambios'}
                                </button>
                            </div>
                        </>
                    )}
                </form>
            </div>
        </div>
    )
}
