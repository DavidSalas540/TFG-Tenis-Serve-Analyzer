import type { AnalysisResult } from '../api/client'

interface Props {
  result:      AnalysisResult
  isDarkMode:  boolean
  accentColor: string
}

// Color según la nota
const GRADE_COLORS: Record<string, string> = {
  A: '#10b981',
  B: '#3b82f6',
  C: '#f59e0b',
  D: '#ef4444',
}

export default function ResultCard({ result, isDarkMode, accentColor }: Props) {
  const gradeColor = GRADE_COLORS[result.grade] ?? accentColor
  const cardClass  = isDarkMode ? 'bg-slate-800/60 border-slate-700' : 'bg-white border-slate-200'
  const muteClass  = isDarkMode ? 'text-slate-400' : 'text-slate-500'
  const badgeClass = isDarkMode ? 'bg-slate-700/50' : 'bg-slate-100'

  // La video_url que viene de Flask es "/api/video/abc.mp4"
  // Necesitamos la URL completa para que el navegador la encuentre
  const videoSrc = `http://localhost:5000${result.video_url}`

  return (
    <div className={`rounded-2xl border p-6 space-y-6 ${cardClass}`}>

      {/* ── Puntuación y nota ── */}
      <div className="flex items-center justify-between">
        <div>
          <p className={`text-sm font-medium mb-1 ${muteClass}`}>Puntuación biomecánica</p>
          <div className="flex items-end gap-3">
            <span className="text-6xl font-bold" style={{ color: gradeColor }}>
              {result.score}
            </span>
            <span className={`text-xl mb-2 ${muteClass}`}>/100</span>
          </div>
        </div>

        {/* Círculo con la letra de nota */}
        <div
          className="w-20 h-20 rounded-full flex items-center justify-center text-4xl font-bold text-white shadow-lg"
          style={{ backgroundColor: gradeColor }}
        >
          {result.grade}
        </div>
      </div>

      {/* ── Tipo de saque ── */}
      <div className="flex gap-3">
        <div className={`flex-1 rounded-xl p-3 text-center ${badgeClass}`}>
          <p className={`text-xs mb-1 ${muteClass}`}>Posición</p>
          <p className="font-semibold">{result.stance}</p>
        </div>
        <div className={`flex-1 rounded-xl p-3 text-center ${badgeClass}`}>
          <p className={`text-xs mb-1 ${muteClass}`}>Efecto</p>
          <p className="font-semibold">{result.effect}</p>
        </div>
      </div>

      {/* ── Vídeo skeleton de MediaPipe ── */}
      <div>
        <p className={`text-sm font-medium mb-3 ${muteClass}`}>Análisis de movimiento</p>
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
