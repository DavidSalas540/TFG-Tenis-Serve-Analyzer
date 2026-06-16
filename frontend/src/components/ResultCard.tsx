import type { AnalysisResult } from '../api/client'
import { API_URL } from '../api/client'

interface Props {
  result:      AnalysisResult
  isDarkMode:  boolean
  accentColor: string
}

const GRADE_COLORS: Record<string, string> = {
  A: '#10b981',
  B: '#3b82f6',
  C: '#f59e0b',
  D: '#ef4444',
}

export default function ResultCard({ result, isDarkMode, accentColor }: Props) {
  const gradeColor = GRADE_COLORS[result.grade] ?? accentColor
  const cardClass  = isDarkMode
    ? 'bg-[#0d0520]/80 border-[#3b0764]/60 backdrop-blur-sm'
    : 'bg-stone-50 border-stone-200'

  const videoSrc = `${API_URL}${result.video_url}`

  return (
    <div className={`rounded-2xl border p-6 space-y-6 ${cardClass}`}>

      {/* ── Puntuación y nota ── */}
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium mb-1 text-[#c084fc]/80">Puntuación biomecánica</p>
          <div className="flex items-end gap-3">
            <span className="text-6xl font-bold" style={{ color: gradeColor }}>
              {result.score}
            </span>
            <span className="text-xl mb-2 text-white/60">/100</span>
          </div>
        </div>

        <div
          className="w-20 h-20 rounded-full flex items-center justify-center text-4xl font-bold text-white shadow-lg"
          style={{ backgroundColor: gradeColor }}
        >
          {result.grade}
        </div>
      </div>

      {/* ── Nivel de análisis ── */}
      {result.nivel && (
        <div className="flex items-center gap-2">
          <span className="text-xs font-semibold text-[#c084fc]/60">Analizado como</span>
          <span className="px-2.5 py-1 rounded-full text-xs font-bold text-white border border-[#7c3aed]/60"
            style={{ background: 'linear-gradient(135deg, #7c3aed40, #c026d340)' }}>
            Nivel {result.nivel} · {(['Iniciación','Básico','Intermedio','Avanzado','Competición'])[result.nivel - 1]}
          </span>
        </div>
      )}

      {/* ── Tipo de saque ── */}
      <div className="flex gap-3">
        <div className="flex-1 rounded-xl p-3 text-center bg-[#1a0a35]/80 border border-[#3b0764]/50">
          <p className="text-xs mb-1 text-[#c084fc]/70">Posición</p>
          <p className="font-bold text-white">{result.stance}</p>
        </div>
        <div className="flex-1 rounded-xl p-3 text-center bg-[#1a0a35]/80 border border-[#3b0764]/50">
          <p className="text-xs mb-1 text-[#c084fc]/70">Efecto</p>
          <p className="font-bold text-white">{result.effect}</p>
        </div>
      </div>

      {/* ── Vídeo skeleton ── */}
      <div>
        <p className="text-sm font-medium mb-3 text-[#c084fc]/80">Análisis de movimiento</p>
        <video
          src={videoSrc}
          controls
          className="w-full rounded-xl"
          style={{ maxHeight: '420px', backgroundColor: '#000' }}
        />
      </div>
    </div>
  )
}
