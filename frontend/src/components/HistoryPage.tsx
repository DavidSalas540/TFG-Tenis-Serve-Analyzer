import { useEffect, useState, useRef } from 'react'
import { Search, FolderPlus, Check, Pencil, Trash2, X } from 'lucide-react'
import {
    getUserAnalyses, getUserCollections,
    addAnalysisToCollection, removeAnalysisFromCollection,
    deleteAnalysis, renameAnalysis,
    type SavedAnalysis, type UserCollection,
} from '../api/client'
import ConfirmModal from './ConfirmModal'

interface Props {
    uid:        string
    isDarkMode: boolean
    onSelect:   (analysis: SavedAnalysis) => void
}

const GRADE_COLORS: Record<string, string> = {
    A: 'text-emerald-400',
    B: 'text-blue-400',
    C: 'text-yellow-400',
    D: 'text-red-400',
}

export default function HistoryPage({ uid, isDarkMode, onSelect }: Props) {
    const [analyses, setAnalyses]       = useState<SavedAnalysis[]>([])
    const [collections, setCollections] = useState<UserCollection[]>([])
    const [loading, setLoading]         = useState(true)
    const [search, setSearch]           = useState('')
    const [dateFrom, setDateFrom]       = useState('')
    const [pickerOpen, setPickerOpen]   = useState<string | null>(null)
    const [renamingId, setRenamingId]     = useState<string | null>(null)
    const [renameVal, setRenameVal]       = useState('')
    const [confirmId, setConfirmId]       = useState<string | null>(null)
    const pickerRef                       = useRef<HTMLDivElement>(null)

    const loadAll = () => {
        Promise.all([getUserAnalyses(uid), getUserCollections(uid)])
            .then(([data, cols]) => {
                data.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
                setAnalyses(data)
                setCollections(cols)
            })
            .finally(() => setLoading(false))
    }

    useEffect(() => { loadAll() }, [uid])

    useEffect(() => {
        const handler = (e: MouseEvent) => {
            if (pickerRef.current && !pickerRef.current.contains(e.target as Node))
                setPickerOpen(null)
        }
        document.addEventListener('mousedown', handler)
        return () => document.removeEventListener('mousedown', handler)
    }, [])

    const handleDelete = async (id: string) => {
        await deleteAnalysis(uid, id)
        setAnalyses(prev => prev.filter(a => a.id !== id))
        setConfirmId(null)
    }

    const handleRenameStart = (a: SavedAnalysis) => {
        setRenamingId(a.id)
        setRenameVal(a.custom_name)
        setPickerOpen(null)
    }

    const handleRenameConfirm = async (id: string) => {
        const name = renameVal.trim()
        if (!name) return
        await renameAnalysis(id, name)
        setAnalyses(prev => prev.map(a => a.id === id ? { ...a, custom_name: name } : a))
        setRenamingId(null)
    }

    const toggleCollection = async (collectionId: string, analysisId: string) => {
        const col = collections.find(c => c.id === collectionId)
        if (!col) return
        if (col.analysis_ids.includes(analysisId)) {
            await removeAnalysisFromCollection(collectionId, analysisId)
        } else {
            await addAnalysisToCollection(collectionId, analysisId)
        }
        getUserCollections(uid).then(setCollections)
    }

    const filtered = analyses.filter(a => {
        const matchName = a.custom_name.toLowerCase().includes(search.toLowerCase())
        const matchDate = dateFrom ? new Date(a.created_at) >= new Date(dateFrom) : true
        return matchName && matchDate
    })

    const inputClass = isDarkMode
        ? 'bg-[#1a0a35]/90 border-[#7c3aed]/70 text-white placeholder-[#c084fc]/60 focus:border-[#c084fc] font-medium'
        : 'bg-amber-50 border-stone-300 text-stone-900 placeholder-stone-400'

    return (
        <div className="max-w-3xl mx-auto py-8 px-4">
            <h2 className="text-4xl font-black mb-6 bg-gradient-to-r from-[#c084fc] via-white to-[#818cf8] bg-clip-text text-transparent"
              style={{ filter: 'drop-shadow(0 0 20px rgba(192,132,252,0.6))' }}>
              Historial de análisis
            </h2>

            {/* Filtros */}
            <div className="flex gap-3 mb-6">
                <div className="relative flex-1">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                    <input type="text" placeholder="Buscar por nombre..."
                        value={search} onChange={e => setSearch(e.target.value)}
                        className={`w-full pl-9 pr-4 py-2.5 rounded-lg border text-sm focus:outline-none ${inputClass}`} />
                </div>
                <input type="date" value={dateFrom} onChange={e => setDateFrom(e.target.value)}
                    className={`px-3 py-2.5 rounded-lg border text-sm focus:outline-none ${inputClass}`} />
            </div>

            {loading && <p className="text-slate-400 text-center py-12">Cargando...</p>}

            {!loading && filtered.length === 0 && (
                <p className="text-white font-bold text-xl text-center py-12">
                    {analyses.length === 0 ? 'Aún no tienes análisis guardados.' : 'No hay resultados para ese filtro.'}
                </p>
            )}

            <div className="space-y-3" ref={pickerRef}>
                {filtered.map(a => (
                    <div key={a.id} className="rounded-xl border bg-[#0d0520]/70 border-[#3b0764]/50 hover:border-[#c084fc]/50 transition-all">

                        {renamingId === a.id ? (
                            /* ── Modo edición nombre ── */
                            <div className="flex items-center gap-2 p-4">
                                <input autoFocus
                                    value={renameVal}
                                    onChange={e => setRenameVal(e.target.value)}
                                    onKeyDown={e => {
                                        if (e.key === 'Enter') handleRenameConfirm(a.id)
                                        if (e.key === 'Escape') setRenamingId(null)
                                    }}
                                    className="flex-1 px-3 py-1.5 rounded-lg bg-[#1a0a35] border border-[#7c3aed]/60 text-white text-sm focus:outline-none focus:border-[#c084fc]"
                                />
                                <button onClick={() => handleRenameConfirm(a.id)}
                                    className="p-1.5 rounded-lg bg-[#7c3aed]/30 hover:bg-[#7c3aed]/60 text-[#c084fc] transition-colors">
                                    <Check className="w-4 h-4" />
                                </button>
                                <button onClick={() => setRenamingId(null)}
                                    className="p-1.5 rounded-lg text-slate-500 hover:text-slate-300 transition-colors">
                                    <X className="w-4 h-4" />
                                </button>
                            </div>
                        ) : (
                            /* ── Vista normal ── */
                            <div className="flex items-center gap-2 p-4">
                                {/* Info clickable */}
                                <button className="flex-1 text-left min-w-0" onClick={() => onSelect(a)}>
                                    <p className="font-semibold text-white truncate">{a.custom_name}</p>
                                    <p className="text-xs mt-0.5 text-slate-400">
                                        {new Date(a.created_at).toLocaleDateString('es-ES', {
                                            day: '2-digit', month: 'short', year: 'numeric'
                                        })}
                                        {' · '}{a.stance} · {a.effect}
                                    </p>
                                </button>

                                {/* Nota */}
                                <div className="text-right shrink-0 cursor-pointer" onClick={() => onSelect(a)}>
                                    <span className={`text-2xl font-bold ${GRADE_COLORS[a.grade]}`}>{a.grade}</span>
                                    <p className="text-xs text-slate-400">{a.score}/100</p>
                                </div>

                                {/* Acciones */}
                                <div className="flex items-center gap-1 shrink-0">
                                    {/* Renombrar */}
                                    <button onClick={() => handleRenameStart(a)} title="Renombrar"
                                        className="p-1.5 rounded-lg text-[#c084fc]/50 hover:text-[#c084fc] hover:bg-[#3b0764]/40 transition-colors">
                                        <Pencil className="w-3.5 h-3.5" />
                                    </button>

                                    {/* Añadir a colección */}
                                    <div className="relative">
                                        <button onClick={() => setPickerOpen(pickerOpen === a.id ? null : a.id)}
                                            title="Añadir a colección"
                                            className="p-1.5 rounded-lg text-[#c084fc]/50 hover:text-[#c084fc] hover:bg-[#3b0764]/40 transition-colors">
                                            <FolderPlus className="w-3.5 h-3.5" />
                                        </button>

                                        {pickerOpen === a.id && (
                                            <div className="absolute right-0 top-8 z-50 w-52 rounded-xl border border-[#3b0764]/60 bg-[#0d0520] shadow-2xl shadow-[#7c3aed]/20 overflow-hidden">
                                                <p className="px-4 py-2.5 text-xs font-semibold text-[#c084fc]/60 border-b border-[#3b0764]/40">
                                                    Guardar en colección
                                                </p>
                                                {collections.length === 0 ? (
                                                    <p className="px-4 py-3 text-xs text-slate-500">No tienes colecciones aún.</p>
                                                ) : (
                                                    collections.map(col => {
                                                        const isIn = col.analysis_ids.includes(a.id)
                                                        return (
                                                            <button key={col.id}
                                                                onClick={() => toggleCollection(col.id, a.id)}
                                                                className="w-full flex items-center justify-between px-4 py-2.5 text-sm text-[#e9d5ff] hover:bg-[#3b0764]/30 transition-colors">
                                                                <span className="truncate">{col.name}</span>
                                                                {isIn && <Check className="w-3.5 h-3.5 text-[#c084fc] shrink-0" />}
                                                            </button>
                                                        )
                                                    })
                                                )}
                                            </div>
                                        )}
                                    </div>

                                    {/* Eliminar */}
                                    <button onClick={() => setConfirmId(a.id)} title="Eliminar"
                                        className="p-1.5 rounded-lg text-red-400/50 hover:text-red-400 hover:bg-red-500/10 transition-colors">
                                        <Trash2 className="w-3.5 h-3.5" />
                                    </button>
                                </div>
                            </div>
                        )}
                    </div>
                ))}
            </div>

            {confirmId && (
                <ConfirmModal
                    message="¿Estás seguro de que quieres eliminar este análisis? Esta acción no se puede deshacer."
                    onConfirm={() => handleDelete(confirmId)}
                    onCancel={() => setConfirmId(null)}
                />
            )}
        </div>
    )
}
