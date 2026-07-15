import { ArrowLeft } from 'lucide-react'
import type { SavedAnalysis } from '../api/client'
import BreakdownTable from './BreakdownTable'

interface Props {
    analysis:   SavedAnalysis
    isDarkMode: boolean
    onBack:     () => void
    backLabel?: string
}

const GRADE_COLORS: Record<string, string> = {
    A: '#10b981',
    B: '#3b82f6',
    C: '#f59e0b',
    D: '#ef4444',
}

export default function AnalysisDetail({ analysis, onBack, backLabel = 'Volver al historial' }: Props) {
    const gradeColor = GRADE_COLORS[analysis.grade] ?? '#10b981'

    return (
        <div className="max-w-3xl mx-auto py-8 px-4">

            <div className="rounded-2xl bg-[#0d0520]/75 border border-[#3b0764]/50 backdrop-blur-sm p-6 mb-6">
                {/* Volver */}
                <button onClick={onBack} className="flex items-center space-x-2 mb-6 text-sm font-medium text-[#c084fc]/70 hover:text-[#c084fc] transition-colors">
                    <ArrowLeft className="w-4 h-4" />
                    <span>{backLabel}</span>
                </button>

                <h2 className="text-2xl font-black mb-1 bg-gradient-to-r from-[#c084fc] via-white to-[#818cf8] bg-clip-text text-transparent"
                    style={{ filter: 'drop-shadow(0 0 12px rgba(192,132,252,0.5))' }}>
                    {analysis.custom_name}
                </h2>
                <p className="text-sm text-[#c084fc]/60">
                    {new Date(analysis.created_at).toLocaleDateString('es-ES', {
                        day: '2-digit', month: 'long', year: 'numeric'
                    })}
                </p>

                {/* Nivel */}
                {analysis.nivel && (
                    <div className="flex items-center gap-2 mt-4">
                        <span className="text-xs font-semibold text-[#c084fc]/60">Analizado como</span>
                        <span className="px-2.5 py-1 rounded-full text-xs font-bold text-white border border-[#7c3aed]/60"
                            style={{ background: 'linear-gradient(135deg, #7c3aed40, #c026d340)' }}>
                            Nivel {analysis.nivel} · {(['Iniciación','Básico','Intermedio','Avanzado','Competición'])[analysis.nivel - 1]}
                        </span>
                    </div>
                )}
            </div>

            {/* Score + nota */}
            <div className="rounded-2xl border bg-[#0d0520]/80 border-[#3b0764]/60 backdrop-blur-sm p-6 mb-6">
                <div className="flex items-center justify-between mb-4">
                    <div>
                        <p className="text-sm font-medium mb-1 text-[#c084fc]/80">Puntuación biomecánica</p>
                        <div className="flex items-end gap-3">
                            <span className="text-6xl font-bold" style={{ color: gradeColor }}>{analysis.score}</span>
                            <span className="text-xl mb-2 text-white/60">/100</span>
                        </div>
                    </div>
                    <div className="w-20 h-20 rounded-full flex items-center justify-center text-4xl font-bold text-white shadow-lg"
                        style={{ backgroundColor: gradeColor }}>
                        {analysis.grade}
                    </div>
                </div>

                <div className="flex gap-3">
                    <div className="flex-1 rounded-xl p-3 text-center bg-[#1a0a35]/80 border border-[#3b0764]/50">
                        <p className="text-xs mb-1 text-[#c084fc]/70">Posición</p>
                        <p className="font-bold text-white">{analysis.stance}</p>
                    </div>
                    <div className="flex-1 rounded-xl p-3 text-center bg-[#1a0a35]/80 border border-[#3b0764]/50">
                        <p className="text-xs mb-1 text-[#c084fc]/70">Efecto</p>
                        <p className="font-bold text-white">{analysis.effect}</p>
                    </div>
                </div>
            </div>

            {/* Métricas */}
            <BreakdownTable breakdown={analysis.breakdown} isDarkMode={true} />
        </div>
    )
}
