import { Lock } from 'lucide-react'
import type { AnalysisResult } from '../api/client'

interface Props {
  breakdown:  AnalysisResult['breakdown']
  isDarkMode: boolean
}

const METRIC_NAMES: Record<string, string> = {
  knee_loading:      'Carga de Rodillas',
  hip_drive:         'Impulso de Caderas',
  jump:              'Despegue',
  shoulder_rotation: 'Rotación de Hombros',
  arm_extension:     'Extensión de Brazo',
  non_dominant_arm:  'Brazo No Dominante',
  trunk_arch:        'Arco de Tronco',
}

const UNLOCK_LEVEL: Record<string, number> = {
  arm_extension:     1,
  non_dominant_arm:  1,
  knee_loading:      2,
  hip_drive:         3,
  trunk_arch:        3,
  shoulder_rotation: 4,
  jump:              5,
}

const LEVEL_NAMES: Record<number, string> = {
  1: 'Iniciación', 2: 'Básico', 3: 'Intermedio', 4: 'Avanzado', 5: 'Competición',
}

function ScoreBar({ score }: { score: number }) {
  const color = score >= 7 ? '#10b981' : score >= 4 ? '#f59e0b' : '#ef4444'
  return (
    <div className="w-full h-2 rounded-full bg-[#1a0a35]">
      <div className="h-2 rounded-full" style={{ width: `${score * 10}%`, backgroundColor: color }} />
    </div>
  )
}

export default function BreakdownTable({ breakdown }: Props) {
  return (
    <div className="rounded-2xl border bg-[#0d0520]/80 border-[#3b0764]/60 backdrop-blur-sm">

      <div className="p-4 border-b border-[#3b0764]/40">
        <h3 className="font-black text-lg bg-gradient-to-r from-[#c084fc] via-white to-[#818cf8] bg-clip-text text-transparent">
          Desglose de métricas
        </h3>
      </div>

      <div className="divide-y divide-[#3b0764]/30">
        {Object.entries(breakdown).map(([key, metric]) => {
          const isActive = metric.active !== false

          if (!isActive) {
            const unlockLevel = UNLOCK_LEVEL[key] ?? 5
            return (
              <div key={key} className="p-4 opacity-40">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <Lock className="w-3.5 h-3.5 text-[#c084fc]/60 shrink-0" />
                    <span className="text-sm font-bold text-white/60">{METRIC_NAMES[key] ?? key}</span>
                  </div>
                  <span className="text-xs font-medium text-[#c084fc]/50 border border-[#3b0764]/50 rounded px-2 py-0.5">
                    Nivel {unlockLevel} — {LEVEL_NAMES[unlockLevel]}
                  </span>
                </div>
                <div className="w-full h-2 rounded-full bg-[#1a0a35]" />
                <p className="text-xs text-[#c084fc]/40 mt-2">{metric.tip}</p>
              </div>
            )
          }

          return (
            <div key={key} className="p-4 space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-sm font-bold text-white">{METRIC_NAMES[key] ?? key}</span>
                <span className="text-sm font-bold text-[#e9d5ff]">{metric.score}/10</span>
              </div>
              <ScoreBar score={metric.score} />
              <p className="text-xs font-semibold text-[#c084fc]">{metric.category}</p>
              <p className="text-xs text-[#e9d5ff]/80">{metric.tip}</p>
            </div>
          )
        })}
      </div>

    </div>
  )
}
