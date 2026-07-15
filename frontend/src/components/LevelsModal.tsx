import { X } from 'lucide-react'
import LevelsPage from './LevelsPage'

interface Props {
    onClose: () => void
}

export default function LevelsModal({ onClose }: Props) {
    return (
        <div className="fixed inset-0 z-50 flex items-start justify-center overflow-y-auto bg-black/70 backdrop-blur-sm py-10 px-4">
            <div className="bg-[#0d0520] border border-[#3b0764]/70 rounded-2xl w-full max-w-5xl shadow-2xl shadow-[#7c3aed]/10 relative">
                <button onClick={onClose}
                    className="absolute top-4 right-4 p-2 rounded-lg text-[#c084fc] hover:bg-[#3b0764]/40 transition-colors z-20">
                    <X className="w-5 h-5" />
                </button>
                <LevelsPage />
            </div>
        </div>
    )
}
