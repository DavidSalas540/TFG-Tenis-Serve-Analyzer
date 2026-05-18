// ===================
// Tipos — forma exacta del JSON que devuelve Flask
// ===================

export interface MetricResult {
    category: string
    score:    number
    tip:      string
}

export interface AnalysisResult {
    stance:    string
    effect:    string
    score:     number
    grade:     string
    video_url: string
    breakdown: {
        knee_loading:      MetricResult
        hip_drive:         MetricResult
        jump:              MetricResult
        shoulder_rotation: MetricResult
        arm_extension:     MetricResult
        non_dominant_arm:  MetricResult
        trunk_arch:        MetricResult
    }
}

// ===================
// Función — envía el vídeo a Flask y devuelve el resultado
// ===================

const API_URL = 'http://localhost:5000'

export async function analyzeVideo(file: File): Promise<AnalysisResult> {
    const form = new FormData()
    form.append('video', file)

    const response = await fetch(`${API_URL}/api/analyze`, {
        method: 'POST',
        body: form,
    })

    if (!response.ok) {
        const error = await response.json()
        throw new Error(error.description || 'Error del servidor')
    }

    return response.json()
}
