import type { AnalysisResult } from '../api/client'

interface Props {
  breakdown:  AnalysisResult['breakdown']
  isDarkMode: boolean
}

// Traducción de claves internas a nombres legibles
const METRIC_NAMES: Record<string, string> = {
  knee_loading:      'Carga de Rodillas',
  hip_drive:         'Impulso de Caderas',
  jump:              'Despegue',
  shoulder_rotation: 'Rotación de Hombros',
  arm_extension:     'Extensión de Brazo',
  non_dominant_arm:  'Brazo No Dominante',
  trunk_arch:        'Arco de Tronco',
}

// Barra de progreso coloreada según el score
function ScoreBar({ score, isDarkMode }: { score: number; isDarkMode: boolean }) {
  const color = score >= 8 ? '#10b981' : score >= 5 ? '#f59e0b' : '#ef4444'
  return (
    <div className={`w-full h-1.5 rounded-full ${isDarkMode ? 'bg-slate-700' : 'bg-slate-200'}`}>
      <div
        className="h-1.5 rounded-full"
        style={{ width: `${score * 10}%`, backgroundColor: color }}
      />
    </div>
  )
}

export default function BreakdownTable({ breakdown, isDarkMode }: Props) {
  const cardClass   = isDarkMode ? 'bg-slate-800/60 border-slate-700' : 'bg-white border-slate-200'
  const divideColor = isDarkMode ? '#334155' : '#f1f5f9'
  const muteClass   = isDarkMode ? 'text-slate-400' : 'text-slate-500'

  return (
    <div className={`rounded-2xl border ${cardClass}`}>

      {/* Cabecera */}
      <div className={`p-4 border-b ${isDarkMode ? 'border-slate-700' : 'border-slate-200'}`}>
        <h3 className="font-semibold">Desglose de métricas</h3>
      </div>

      {/* Una fila por métrica */}
      <div className="divide-y" style={{ borderColor: divideColor }}>
        {Object.entries(breakdown).map(([key, metric]) => (
          <div key={key} className="p-4 space-y-2">

            {/* Nombre + score numérico */}
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium">{METRIC_NAMES[key] ?? key}</span>
              <span className="text-sm font-bold">{metric.score}/10</span>
            </div>

            {/* Barra visual */}
            <ScoreBar score={metric.score} isDarkMode={isDarkMode} />

            {/* Categoría */}
            <p className={`text-xs font-medium ${muteClass}`}>{metric.category}</p>

            {/* Consejo */}
            <p className={`text-xs ${muteClass}`}>{metric.tip}</p>
          </div>
        ))}
      </div>

    </div>
  )
}
