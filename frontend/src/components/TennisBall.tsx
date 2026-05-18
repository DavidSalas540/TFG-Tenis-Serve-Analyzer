export function TennisBall({ className = 'w-6 h-6' }: { className?: string }) {
    return (
        <svg viewBox="0 0 100 100" className={className} fill="none">
            <circle cx="50" cy="50" r="45" stroke="currentColor" strokeWidth="2" fill="#ffd700" />
            <path
                d="M 50 10 Q 50 30 50 50 Q 50 70 50 90"
                stroke="white"
                strokeWidth="3"
                strokeLinecap="round"
            />
            <path
                d="M 30 40 Q 40 45 50 50 Q 40 55 30 60"
                stroke="white"
                strokeWidth="2.5"
                strokeLinecap="round"
            />
            <path
                d="M 70 40 Q 60 45 50 50 Q 60 55 70 60"
                stroke="white"
                strokeWidth="2.5"
                strokeLinecap="round"
            />
        </svg>
    );
}
