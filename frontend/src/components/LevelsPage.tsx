import { Check, Lock } from 'lucide-react'

interface Props {
    userNivel?: number
}

const LEVELS = [
    { n: 1, name: 'Iniciación',  color: '#6366f1', glow: 'rgba(99,102,241,0.7)',   desc: 'Aprende a colocar correctamente el brazo dominante y a lanzar la pelota.' },
    { n: 2, name: 'Básico',      color: '#8b5cf6', glow: 'rgba(139,92,246,0.7)',   desc: 'Añade la fase de carga con flexión de rodillas para generar potencia.' },
    { n: 3, name: 'Intermedio',  color: '#a855f7', glow: 'rgba(168,85,247,0.7)',   desc: 'Incorpora el impulso de caderas y el arco del tronco para mayor explosividad.' },
    { n: 4, name: 'Avanzado',    color: '#c026d3', glow: 'rgba(192,38,211,0.7)',   desc: 'Domina la rotación de hombros para maximizar la velocidad.' },
    { n: 5, name: 'Competición', color: '#f59e0b', glow: 'rgba(245,158,11,0.75)',  desc: 'Análisis completo: todas las métricas, incluido el despegue y el salto.' },
]

const METRICS = [
    { key: 'arm_extension',     name: 'Extensión de Brazo',    desc: 'Ángulo del codo dominante en el impacto',  unlockLevel: 1 },
    { key: 'non_dominant_arm',  name: 'Brazo No Dominante',    desc: 'Posición del brazo de lanzamiento (toss)', unlockLevel: 1 },
    { key: 'knee_loading',      name: 'Carga de Rodillas',     desc: 'Flexión de rodillas en la fase de carga',  unlockLevel: 2 },
    { key: 'hip_drive',         name: 'Impulso de Caderas',    desc: 'Proyección de caderas hacia la red',       unlockLevel: 3 },
    { key: 'trunk_arch',        name: 'Arco de Tronco',        desc: 'Forma de arco del cuerpo en el impacto',   unlockLevel: 3 },
    { key: 'shoulder_rotation', name: 'Rotación de Hombros',   desc: 'El giro que hace el hombro respecto a las caderas', unlockLevel: 4 },
    { key: 'jump',              name: 'Despegue / Salto',      desc: 'Altura de salto normalizada por cadera',   unlockLevel: 5 },
]

export default function LevelsPage({ userNivel }: Props) {
    return (
        <div className="max-w-5xl mx-auto py-8 px-4" style={{ position: 'relative', zIndex: 10 }}>

            {/* ── Título ── */}
            <h2 className="text-4xl font-black mb-2 bg-gradient-to-r from-[#c084fc] via-white to-[#818cf8] bg-clip-text text-transparent"
                style={{ filter: 'drop-shadow(0 0 20px rgba(192,132,252,0.6))' }}>
                Sistema de Niveles
            </h2>
            <p className="text-slate-300 mb-2 max-w-2xl text-sm leading-relaxed">
                Cada nivel desbloquea nuevas métricas biomecánicas. Empieza dominando los fundamentos
                del brazo y ve añadiendo complejidad conforme mejoras tu técnica.
            </p>
            {userNivel && (
                <div className="flex items-center gap-2 mb-8">
                    <span className="text-sm text-slate-300 font-medium">Tu nivel actual:</span>
                    <span className="px-3 py-1 rounded-full text-sm font-bold text-white"
                        style={{
                            background: `linear-gradient(135deg, ${LEVELS[userNivel - 1].color}, ${LEVELS[userNivel - 1].color}bb)`,
                            boxShadow:  `0 0 14px ${LEVELS[userNivel - 1].glow}`,
                        }}>
                        Nivel {userNivel} — {LEVELS[userNivel - 1].name}
                    </span>
                </div>
            )}

            {/* ── Tabla ── */}
            <div className="rounded-2xl overflow-hidden overflow-x-auto mb-10"
                 style={{ border: '1px solid #7c3aed', boxShadow: '0 0 40px rgba(124,58,237,0.25)' }}>

                {/* Cabecera de niveles */}
                <div className="grid min-w-[640px]"
                     style={{ gridTemplateColumns: '210px repeat(5, 1fr)', gap: '1px', backgroundColor: '#7c3aed' }}>

                    <div className="px-5 py-5" style={{ backgroundColor: '#1a0845' }}>
                        <span className="text-xs font-bold uppercase tracking-widest text-slate-300">Métrica</span>
                    </div>

                    {LEVELS.map(level => {
                        const isUser = level.n === userNivel
                        return (
                            <div key={level.n} className="px-3 py-5 text-center"
                                 style={{
                                     backgroundColor: isUser ? `${level.color}30` : '#1a0845',
                                     outline: isUser ? `2px solid ${level.color}` : 'none',
                                     outlineOffset: '-2px',
                                 }}>
                                <div className="text-2xl font-black"
                                     style={{ color: level.color, filter: `drop-shadow(0 0 10px ${level.glow})` }}>
                                    N{level.n}
                                </div>
                                <div className="text-sm font-semibold text-white mt-1">{level.name}</div>
                                {isUser && (
                                    <div className="text-[10px] font-black uppercase tracking-widest mt-1"
                                         style={{ color: level.color }}>
                                        ← Tu nivel
                                    </div>
                                )}
                            </div>
                        )
                    })}
                </div>

                {/* Filas de métricas */}
                {METRICS.map(metric => (
                    <div key={metric.key}
                         className="grid min-w-[640px]"
                         style={{ gridTemplateColumns: '210px repeat(5, 1fr)', gap: '1px', backgroundColor: '#4c1d95' }}>

                        {/* Nombre métrica */}
                        <div className="px-5 py-4" style={{ backgroundColor: '#1a0845' }}>
                            <p className="text-sm font-bold text-white">{metric.name}</p>
                            <p className="text-xs text-slate-400 mt-1 leading-snug">{metric.desc}</p>
                        </div>

                        {/* Celdas */}
                        {LEVELS.map(level => {
                            const isNew    = level.n === metric.unlockLevel
                            const isActive = level.n > metric.unlockLevel
                            const isLocked = level.n < metric.unlockLevel
                            const isUser   = level.n === userNivel

                            return (
                                <div key={level.n}
                                     className="flex flex-col items-center justify-center py-4 gap-1.5"
                                     style={{ backgroundColor: isUser ? `${level.color}20` : '#160638' }}>

                                    {isNew && (
                                        <>
                                            <div className="w-9 h-9 rounded-full flex items-center justify-center"
                                                 style={{
                                                     background:  level.color,
                                                     boxShadow:   `0 0 18px ${level.glow}, 0 0 6px ${level.color}`,
                                                 }}>
                                                <Check className="w-5 h-5 text-white" strokeWidth={3} />
                                            </div>
                                            <span className="text-[10px] font-black uppercase tracking-widest"
                                                  style={{ color: level.color, filter: `drop-shadow(0 0 4px ${level.glow})` }}>
                                                Nuevo
                                            </span>
                                        </>
                                    )}

                                    {isActive && (
                                        <div className="w-8 h-8 rounded-full flex items-center justify-center"
                                             style={{
                                                 border:          `2px solid ${level.color}`,
                                                 backgroundColor: `${level.color}25`,
                                             }}>
                                            <Check className="w-4 h-4" style={{ color: level.color }} strokeWidth={2.5} />
                                        </div>
                                    )}

                                    {isLocked && (
                                        <div className="w-8 h-8 rounded-full flex items-center justify-center"
                                             style={{
                                                 border:          '2px solid #6b3fa0',
                                                 backgroundColor: '#2a0f5a',
                                             }}>
                                            <Lock className="w-4 h-4 text-slate-400" />
                                        </div>
                                    )}
                                </div>
                            )
                        })}
                    </div>
                ))}
            </div>

            {/* ── Tarjetas de nivel ── */}
            <h3 className="text-xl font-black mb-4 text-white">¿Qué trabajas en cada nivel?</h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3">
                {LEVELS.map(level => {
                    const newMetrics = METRICS.filter(m => m.unlockLevel === level.n)
                    const isUser     = level.n === userNivel
                    return (
                        <div key={level.n} className="rounded-xl p-4 relative"
                             style={{
                                 border:          `1px solid ${isUser ? level.color : '#4c1d95'}`,
                                 backgroundColor: isUser ? `${level.color}20` : '#160638',
                                 boxShadow:       isUser ? `0 0 24px ${level.glow}` : 'none',
                             }}>
                            {isUser && (
                                <div className="absolute top-2 right-2 text-[9px] font-black uppercase tracking-widest px-1.5 py-0.5 rounded"
                                     style={{ background: level.color, color: '#fff' }}>
                                    Tu nivel
                                </div>
                            )}
                            <div className="text-2xl font-black mb-1"
                                 style={{ color: level.color, filter: `drop-shadow(0 0 8px ${level.glow})` }}>
                                N{level.n}
                            </div>
                            <div className="text-sm font-bold text-white mb-2">{level.name}</div>
                            <p className="text-xs text-slate-300 leading-relaxed mb-3">{level.desc}</p>
                            <div className="space-y-1.5">
                                {newMetrics.map(m => (
                                    <div key={m.key} className="flex items-center gap-2">
                                        <div className="w-1.5 h-1.5 rounded-full shrink-0" style={{ background: level.color }} />
                                        <span className="text-xs font-semibold text-slate-200">{m.name}</span>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )
                })}
            </div>

        </div>
    )
}
