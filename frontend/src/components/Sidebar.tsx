import { Home, History, FolderOpen, Trophy, X } from 'lucide-react'

type View = 'home' | 'history' | 'collections' | 'levels'

interface Props {
    isOpen:      boolean
    onClose:     () => void
    currentView: View
    onNavigate:  (view: View) => void
    isDarkMode:  boolean
}

export default function Sidebar({ isOpen, onClose, currentView, onNavigate }: Props) {
    if (!isOpen) return null

    const handleNav = (view: View) => {
        onNavigate(view)
        onClose()
    }

    const itemClass = (view: View) => {
        const active = currentView === view
        return `flex items-center space-x-3 w-full px-4 py-3 rounded-xl font-medium transition-all ${
            active
                ? 'bg-[#7c3aed]/20 text-[#c084fc] border border-[#7c3aed]/40'
                : 'text-slate-400 hover:bg-[#3b0764]/30 hover:text-[#c084fc]'
        }`
    }

    return (
        <div className="fixed inset-0 z-50 flex">
            <div className="flex-1 bg-black/60 backdrop-blur-sm" onClick={onClose} />

            <div className="absolute left-0 top-0 h-full w-64 bg-[#0d0520] border-r border-[#3b0764]/60 shadow-2xl shadow-[#7c3aed]/10">

                <div className="flex items-center justify-between px-4 py-5 border-b border-[#3b0764]/40">
                    <span className="font-bold text-lg bg-gradient-to-r from-[#c084fc] to-[#818cf8] bg-clip-text text-transparent">Menú</span>
                    <button onClick={onClose} className="p-1.5 rounded-lg text-[#c084fc]/50 hover:text-[#c084fc] hover:bg-[#3b0764]/40 transition-colors">
                        <X className="w-5 h-5" />
                    </button>
                </div>

                <nav className="p-3 space-y-1">
                    <button onClick={() => handleNav('home')} className={itemClass('home')}>
                        <Home className="w-5 h-5" />
                        <span>Inicio</span>
                    </button>
                    <button onClick={() => handleNav('history')} className={itemClass('history')}>
                        <History className="w-5 h-5" />
                        <span>Historial</span>
                    </button>
                    <button onClick={() => handleNav('collections')} className={itemClass('collections')}>
                        <FolderOpen className="w-5 h-5" />
                        <span>Colecciones</span>
                    </button>
                    <button onClick={() => handleNav('levels')} className={itemClass('levels')}>
                        <Trophy className="w-5 h-5" />
                        <span>Niveles</span>
                    </button>
                </nav>
            </div>
        </div>
    )
}
