import { useEffect, useState } from 'react'
import { Plus, Pencil, Trash2, ArrowLeft, FolderOpen, X, Check, Search } from 'lucide-react'
import ConfirmModal from './ConfirmModal'
import {
    getUserCollections, createCollection, renameCollection,
    deleteCollection, removeAnalysisFromCollection, addAnalysisToCollection,
    getUserAnalyses,
    type UserCollection, type SavedAnalysis,
} from '../api/client'

interface Props {
    uid: string
    onSelectAnalysis: (analysis: SavedAnalysis) => void
}

const GRADE_COLORS: Record<string, string> = {
    A: 'text-emerald-400',
    B: 'text-blue-400',
    C: 'text-yellow-400',
    D: 'text-red-400',
}

const inputClass = 'px-3 py-2 rounded-lg bg-[#1a0a35] border border-[#7c3aed]/50 text-white placeholder-[#c084fc]/40 focus:outline-none focus:border-[#c084fc] text-sm transition-colors'

export default function CollectionsPage({ uid, onSelectAnalysis }: Props) {
    const [collections, setCollections] = useState<UserCollection[]>([])
    const [allAnalyses, setAllAnalyses] = useState<SavedAnalysis[]>([])
    const [loading, setLoading]         = useState(true)
    const [selected, setSelected]       = useState<UserCollection | null>(null)
    const [createError, setCreateError] = useState('')

    const [newName, setNewName]         = useState('')
    const [creating, setCreating]       = useState(false)

    const [renaming, setRenaming]       = useState<string | null>(null)
    const [renameVal, setRenameVal]     = useState('')

    const [confirmId, setConfirmId]     = useState<string | null>(null)

    const [addModalOpen, setAddModalOpen]   = useState(false)
    const [modalSearch, setModalSearch]     = useState('')
    const [modalDate, setModalDate]         = useState('')
    const [selectedIds, setSelectedIds]     = useState<Set<string>>(new Set())
    const [addingIds, setAddingIds]         = useState(false)

    const load = (keepLoading = false) => {
        if (!keepLoading) setLoading(true)
        Promise.all([getUserCollections(uid), getUserAnalyses(uid)])
            .then(([cols, analyses]) => {
                cols.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
                setCollections(cols)
                setAllAnalyses(analyses)
                if (selected) {
                    const updated = cols.find(c => c.id === selected.id)
                    setSelected(updated ?? null)
                }
            })
            .finally(() => setLoading(false))
    }

    useEffect(() => { load() }, [uid])

    const handleCreate = async () => {
        const name = newName.trim()
        if (!name) return
        setCreateError('')
        try {
            await createCollection(uid, name)
            setNewName(''); setCreating(false)
            load(true)
        } catch (e) {
            setCreateError(e instanceof Error ? e.message : 'Error al crear la colección. Revisa las reglas de Firestore.')
        }
    }

    const handleRename = async (id: string) => {
        const name = renameVal.trim()
        if (!name) return
        try {
            await renameCollection(id, name)
            setRenaming(null)
            load(true)
        } catch { /* silent */ }
    }

    const handleDelete = async (id: string) => {
        await deleteCollection(id)
        if (selected?.id === id) setSelected(null)
        setConfirmId(null)
        load(true)
    }

    const handleRemoveAnalysis = async (collectionId: string, analysisId: string) => {
        await removeAnalysisFromCollection(collectionId, analysisId)
        load(true)
    }

    const analysesInCollection = (col: UserCollection) =>
        allAnalyses.filter(a => col.analysis_ids.includes(a.id))

    const openAddModal = () => {
        setModalSearch('')
        setModalDate('')
        setSelectedIds(new Set())
        setAddModalOpen(true)
    }

    const handleConfirmAdd = async () => {
        if (!selected || selectedIds.size === 0) return
        setAddingIds(true)
        await Promise.all([...selectedIds].map(id => addAnalysisToCollection(selected.id, id)))
        setAddingIds(false)
        setAddModalOpen(false)
        load(true)
    }

    const toggleId = (id: string, alreadyIn: boolean) => {
        if (alreadyIn) return
        setSelectedIds(prev => {
            const next = new Set(prev)
            next.has(id) ? next.delete(id) : next.add(id)
            return next
        })
    }

    const modalFiltered = allAnalyses.filter(a => {
        const matchName = a.custom_name.toLowerCase().includes(modalSearch.toLowerCase())
        const matchDate = modalDate ? new Date(a.created_at) >= new Date(modalDate) : true
        return matchName && matchDate
    })

    if (loading) return <p className="text-slate-400 text-center py-20">Cargando...</p>

    // ── Vista detalle de una colección ──
    if (selected) {
        const items = analysesInCollection(selected)
        return (
            <div className="max-w-3xl mx-auto py-8 px-4">
                <button onClick={() => setSelected(null)}
                    className="flex items-center space-x-2 mb-6 text-sm font-medium text-[#c084fc]/70 hover:text-[#c084fc] transition-colors">
                    <ArrowLeft className="w-4 h-4" />
                    <span>Volver a colecciones</span>
                </button>

                <div className="flex items-center justify-between mb-6">
                    {renaming === selected.id ? (
                        <div className="flex items-center gap-2">
                            <input autoFocus value={renameVal} onChange={e => setRenameVal(e.target.value)}
                                onKeyDown={e => e.key === 'Enter' && handleRename(selected.id)}
                                className={inputClass} />
                            <button onClick={() => handleRename(selected.id)}
                                className="p-2 rounded-lg bg-[#7c3aed]/30 hover:bg-[#7c3aed]/50 text-[#c084fc] transition-colors">
                                <Check className="w-4 h-4" />
                            </button>
                            <button onClick={() => setRenaming(null)}
                                className="p-2 rounded-lg text-slate-500 hover:text-slate-300 transition-colors">
                                <X className="w-4 h-4" />
                            </button>
                        </div>
                    ) : (
                        <h2 className="text-3xl font-black bg-gradient-to-r from-[#c084fc] via-white to-[#818cf8] bg-clip-text text-transparent"
                            style={{ filter: 'drop-shadow(0 0 16px rgba(192,132,252,0.5))' }}>
                            {selected.name}
                        </h2>
                    )}
                    <div className="flex items-center gap-2">
                        <button onClick={openAddModal}
                            className="flex items-center gap-1.5 px-3 py-2 rounded-lg text-white font-semibold text-sm transition-all hover:opacity-90 hover:scale-105 shadow-lg shadow-[#7c3aed]/30"
                            style={{ background: 'linear-gradient(135deg, #7c3aed, #c026d3)' }}>
                            <Plus className="w-4 h-4" />
                            Añadir análisis
                        </button>
                        <button onClick={() => { setRenaming(selected.id); setRenameVal(selected.name) }}
                            className="p-2 rounded-lg text-[#c084fc]/60 hover:text-[#c084fc] hover:bg-[#3b0764]/40 transition-colors">
                            <Pencil className="w-4 h-4" />
                        </button>
                        <button onClick={() => setConfirmId(selected.id)}
                            className="p-2 rounded-lg text-red-400/60 hover:text-red-400 hover:bg-red-500/10 transition-colors">
                            <Trash2 className="w-4 h-4" />
                        </button>
                    </div>
                </div>

                {items.length === 0 ? (
                    <p className="text-white font-bold text-xl text-center py-12">
                        Esta colección está vacía. Añade análisis desde el Historial.
                    </p>
                ) : (
                    <div className="space-y-3">
                        {items.map(a => (
                            <div key={a.id}
                                className="w-full text-left rounded-xl border bg-[#0d0520]/70 border-[#3b0764]/50 hover:border-[#c084fc]/50 flex items-center justify-between transition-all">
                                <button className="flex-1 text-left p-4 min-w-0" onClick={() => onSelectAnalysis(a)}>
                                    <p className="font-semibold text-white">{a.custom_name}</p>
                                    <p className="text-xs mt-0.5 text-slate-400">
                                        {new Date(a.created_at).toLocaleDateString('es-ES', {
                                            day: '2-digit', month: 'short', year: 'numeric'
                                        })}
                                        {' · '}{a.stance} · {a.effect}
                                    </p>
                                </button>
                                <div className="flex items-center gap-4 pr-4 shrink-0">
                                    <div className="text-right cursor-pointer" onClick={() => onSelectAnalysis(a)}>
                                        <span className={`text-2xl font-bold ${GRADE_COLORS[a.grade]}`}>{a.grade}</span>
                                        <p className="text-xs text-slate-400">{a.score}/100</p>
                                    </div>
                                    <button onClick={() => handleRemoveAnalysis(selected.id, a.id)}
                                        title="Quitar de colección"
                                        className="p-1.5 rounded-lg text-red-400/60 hover:text-red-400 hover:bg-red-500/10 transition-colors">
                                        <X className="w-4 h-4" />
                                    </button>
                                </div>
                            </div>
                        ))}
                    </div>
                )}

                {confirmId && (
                    <ConfirmModal
                        message="¿Eliminar esta colección? Los análisis no se borrarán del historial."
                        onConfirm={() => handleDelete(confirmId)}
                        onCancel={() => setConfirmId(null)}
                    />
                )}

                {addModalOpen && (
                    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm">
                        <div className="bg-[#0d0520] border border-[#3b0764]/70 rounded-2xl w-full max-w-xl mx-4 shadow-2xl shadow-[#7c3aed]/10 flex flex-col" style={{ maxHeight: '80vh' }}>

                            {/* Header */}
                            <div className="flex items-center justify-between px-6 py-5 border-b border-[#3b0764]/40 shrink-0">
                                <h3 className="text-lg font-bold bg-gradient-to-r from-[#c084fc] to-[#818cf8] bg-clip-text text-transparent">
                                    Añadir análisis a "{selected.name}"
                                </h3>
                                <button onClick={() => setAddModalOpen(false)}
                                    className="p-1.5 rounded-lg text-[#c084fc]/50 hover:text-[#c084fc] hover:bg-[#3b0764]/40 transition-colors">
                                    <X className="w-5 h-5" />
                                </button>
                            </div>

                            {/* Filtros */}
                            <div className="flex gap-3 px-6 py-4 shrink-0">
                                <div className="relative flex-1">
                                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                                    <input type="text" placeholder="Buscar por nombre..."
                                        value={modalSearch} onChange={e => setModalSearch(e.target.value)}
                                        className="w-full pl-9 pr-4 py-2.5 rounded-lg border bg-[#1a0a35]/90 border-[#7c3aed]/70 text-white placeholder-[#c084fc]/60 focus:outline-none focus:border-[#c084fc] text-sm" />
                                </div>
                                <input type="date" value={modalDate} onChange={e => setModalDate(e.target.value)}
                                    className="px-3 py-2.5 rounded-lg border bg-[#1a0a35]/90 border-[#7c3aed]/70 text-white focus:outline-none focus:border-[#c084fc] text-sm" />
                            </div>

                            {/* Lista */}
                            <div className="flex-1 overflow-y-auto px-6 space-y-2 pb-4">
                                {modalFiltered.length === 0 && (
                                    <p className="text-slate-400 text-center py-8">No hay análisis que coincidan.</p>
                                )}
                                {modalFiltered.map(a => {
                                    const alreadyIn = selected.analysis_ids.includes(a.id)
                                    const checked   = alreadyIn || selectedIds.has(a.id)
                                    return (
                                        <button key={a.id} onClick={() => toggleId(a.id, alreadyIn)}
                                            disabled={alreadyIn}
                                            className={`w-full flex items-center gap-3 p-3 rounded-xl border text-left transition-all ${
                                                alreadyIn
                                                    ? 'opacity-40 cursor-default border-[#3b0764]/30 bg-[#0d0520]/50'
                                                    : checked
                                                    ? 'border-[#c084fc]/60 bg-[#3b0764]/20'
                                                    : 'border-[#3b0764]/50 bg-[#0d0520]/70 hover:border-[#c084fc]/40'
                                            }`}>
                                            {/* Checkbox */}
                                            <div className={`w-5 h-5 rounded flex items-center justify-center shrink-0 border-2 transition-all ${
                                                checked ? 'bg-[#7c3aed] border-[#7c3aed]' : 'border-[#7c3aed]/50'
                                            }`}>
                                                {checked && <Check className="w-3 h-3 text-white" />}
                                            </div>
                                            {/* Info */}
                                            <div className="flex-1 min-w-0">
                                                <p className="font-semibold text-white text-sm truncate">{a.custom_name}</p>
                                                <p className="text-xs text-slate-400 mt-0.5">
                                                    {new Date(a.created_at).toLocaleDateString('es-ES', { day: '2-digit', month: 'short', year: 'numeric' })}
                                                    {' · '}{a.stance} · {a.effect}
                                                </p>
                                            </div>
                                            {/* Nota */}
                                            <div className="text-right shrink-0">
                                                <span className={`text-xl font-bold ${GRADE_COLORS[a.grade]}`}>{a.grade}</span>
                                                <p className="text-xs text-slate-400">{a.score}/100</p>
                                            </div>
                                        </button>
                                    )
                                })}
                            </div>

                            {/* Footer */}
                            <div className="flex items-center justify-between px-6 py-4 border-t border-[#3b0764]/40 shrink-0">
                                <span className="text-sm text-[#c084fc]/70">
                                    {selectedIds.size} seleccionado{selectedIds.size !== 1 ? 's' : ''}
                                </span>
                                <div className="flex gap-3">
                                    <button onClick={() => setAddModalOpen(false)}
                                        className="px-4 py-2 rounded-lg text-slate-400 hover:text-white text-sm transition-colors">
                                        Cancelar
                                    </button>
                                    <button onClick={handleConfirmAdd} disabled={selectedIds.size === 0 || addingIds}
                                        className="px-5 py-2 rounded-lg text-white font-semibold text-sm transition-all hover:opacity-90 disabled:opacity-40"
                                        style={{ background: 'linear-gradient(135deg, #7c3aed, #c026d3)' }}>
                                        {addingIds ? 'Añadiendo...' : 'Añadir'}
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        )
    }


    // ── Vista lista de colecciones ──
    return (
        <div className="max-w-3xl mx-auto py-8 px-4">
            <div className="flex items-center justify-between mb-6">
                <h2 className="text-4xl font-black bg-gradient-to-r from-[#c084fc] via-white to-[#818cf8] bg-clip-text text-transparent"
                    style={{ filter: 'drop-shadow(0 0 20px rgba(192,132,252,0.6))' }}>
                    Colecciones
                </h2>
                <button onClick={() => setCreating(true)}
                    className="flex items-center gap-2 px-4 py-2.5 rounded-lg text-white font-bold text-sm transition-all hover:opacity-90 hover:scale-105 shadow-lg shadow-[#7c3aed]/30"
                    style={{ background: 'linear-gradient(135deg, #7c3aed, #c026d3)' }}>
                    <Plus className="w-4 h-4" />
                    Nueva colección
                </button>
            </div>

            {creating && (
                <div className="mb-4 p-4 rounded-xl" style={{ backgroundColor: '#1a0845', border: '1px solid #7c3aed', boxShadow: '0 0 20px rgba(124,58,237,0.3)' }}>
                    <div className="flex items-center gap-2">
                        <input autoFocus placeholder="Nombre de la colección..."
                            value={newName} onChange={e => setNewName(e.target.value)}
                            onKeyDown={e => e.key === 'Enter' && handleCreate()}
                            className="flex-1 px-4 py-2.5 rounded-lg text-white text-sm focus:outline-none placeholder-[#c084fc]/50 font-medium"
                            style={{ backgroundColor: '#2a0f5a', border: '1px solid #7c3aed' }} />
                        <button onClick={handleCreate}
                            className="flex items-center gap-1.5 px-4 py-2.5 rounded-lg text-white font-bold text-sm transition-all hover:opacity-90 hover:scale-105 shadow-lg shadow-[#7c3aed]/30"
                            style={{ background: 'linear-gradient(135deg, #7c3aed, #c026d3)' }}>
                            <Check className="w-4 h-4" />
                            Crear
                        </button>
                        <button onClick={() => { setCreating(false); setNewName(''); setCreateError('') }}
                            className="p-2.5 rounded-lg transition-colors text-white font-bold"
                            style={{ backgroundColor: '#2a0f5a', border: '1px solid #6b3fa0' }}>
                            <X className="w-4 h-4" />
                        </button>
                    </div>
                    {createError && <p className="mt-2 text-red-400 text-xs">{createError}</p>}
                </div>
            )}

            {collections.length === 0 && !creating && (
                <p className="font-bold text-xl text-center py-12 bg-gradient-to-r from-[#c084fc] via-white to-[#818cf8] bg-clip-text text-transparent"
                   style={{ filter: 'drop-shadow(0 0 20px rgba(192,132,252,0.8))' }}>
                    Aún no tienes colecciones. Crea una con el botón de arriba.
                </p>
            )}

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 overflow-y-auto">
                {collections.map(col => {
                    const count = col.analysis_ids.length
                    return (
                        <div key={col.id}
                            className="rounded-xl border bg-[#0d0520]/80 border-[#3b0764]/60 backdrop-blur-sm p-5 flex flex-col gap-3">

                            {renaming === col.id ? (
                                <div className="flex items-center gap-2">
                                    <input autoFocus value={renameVal} onChange={e => setRenameVal(e.target.value)}
                                        onKeyDown={e => e.key === 'Enter' && handleRename(col.id)}
                                        className={`flex-1 ${inputClass}`} />
                                    <button onClick={() => handleRename(col.id)}
                                        className="p-1.5 rounded-lg bg-[#7c3aed]/30 hover:bg-[#7c3aed]/50 text-[#c084fc] transition-colors">
                                        <Check className="w-3.5 h-3.5" />
                                    </button>
                                    <button onClick={() => setRenaming(null)}
                                        className="p-1.5 rounded-lg text-slate-500 hover:text-slate-300 transition-colors">
                                        <X className="w-3.5 h-3.5" />
                                    </button>
                                </div>
                            ) : (
                                <div className="flex items-start justify-between">
                                    <div>
                                        <p className="font-bold text-white text-base">{col.name}</p>
                                        <p className="text-xs text-[#c084fc]/60 mt-0.5">
                                            {count} {count === 1 ? 'análisis' : 'análisis'}
                                        </p>
                                    </div>
                                    <div className="flex items-center gap-1">
                                        <button onClick={() => { setRenaming(col.id); setRenameVal(col.name) }}
                                            className="p-1.5 rounded-lg text-[#c084fc]/50 hover:text-[#c084fc] hover:bg-[#3b0764]/40 transition-colors">
                                            <Pencil className="w-3.5 h-3.5" />
                                        </button>
                                        <button onClick={() => setConfirmId(col.id)}
                                            className="p-1.5 rounded-lg text-red-400/50 hover:text-red-400 hover:bg-red-500/10 transition-colors">
                                            <Trash2 className="w-3.5 h-3.5" />
                                        </button>
                                    </div>
                                </div>
                            )}

                            <button onClick={() => setSelected(col)}
                                className="flex items-center gap-2 text-sm font-medium text-[#c084fc]/70 hover:text-[#c084fc] transition-colors">
                                <FolderOpen className="w-4 h-4" />
                                <span>Abrir colección</span>
                            </button>
                        </div>
                    )
                })}
            </div>

            {confirmId && (
                <ConfirmModal
                    message="¿Eliminar esta colección? Los análisis no se borrarán del historial."
                    onConfirm={() => handleDelete(confirmId)}
                    onCancel={() => setConfirmId(null)}
                />
            )}
        </div>
    )
}
