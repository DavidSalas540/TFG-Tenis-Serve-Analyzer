interface Props {
    message:   string
    onConfirm: () => void
    onCancel:  () => void
}

export default function ConfirmModal({ message, onConfirm, onCancel }: Props) {
    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm">
            <div className="bg-[#0d0520] border border-[#3b0764]/70 rounded-2xl w-full max-w-sm mx-4 shadow-2xl shadow-[#7c3aed]/10 p-6">
                <p className="text-white font-semibold text-base mb-6 text-center leading-relaxed">
                    {message}
                </p>
                <div className="flex gap-3">
                    <button onClick={onCancel}
                        className="flex-1 py-2.5 rounded-lg font-semibold text-sm text-[#c084fc] border border-[#7c3aed]/50 hover:bg-[#3b0764]/30 transition-colors">
                        Cancelar
                    </button>
                    <button onClick={onConfirm}
                        className="flex-1 py-2.5 rounded-lg font-semibold text-sm text-white transition-all hover:opacity-90"
                        style={{ background: 'linear-gradient(135deg, #7c3aed, #c026d3)' }}>
                        Eliminar
                    </button>
                </div>
            </div>
        </div>
    )
}
