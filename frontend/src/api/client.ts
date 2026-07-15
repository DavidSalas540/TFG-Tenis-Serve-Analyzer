import { auth, db } from '../firebase'
import { collection, addDoc, getDocs, query, where, serverTimestamp, doc, updateDoc, deleteDoc, arrayUnion, arrayRemove } from 'firebase/firestore'

// ===================
// Tipos
// ===================

export interface MetricResult {
    category: string
    score:    number
    tip:      string
    active?:  boolean
}

export interface AnalysisResult {
    stance:    string
    effect:    string
    score:     number
    grade:     string
    video_url: string
    nivel?:    number
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

export interface SavedAnalysis {
    id:          string
    uid:         string
    filename:    string
    custom_name: string
    score:       number
    grade:       string
    stance:      string
    effect:      string
    nivel?:      number
    breakdown:   AnalysisResult['breakdown']
    created_at:  string
}

export const API_URL = 'http://localhost:5000'

// ===================
// Helper — token Firebase
// ===================

async function getAuthHeader(): Promise<string> {
    const user = auth.currentUser
    if (!user) throw new Error('No hay sesión activa.')
    const token = await user.getIdToken()
    return `Bearer ${token}`
}

// ===================
// Flask — analizar vídeo
// ===================

export async function analyzeVideo(file: File, nivel: number = 5): Promise<AnalysisResult> {
    const form = new FormData()
    form.append('video', file)
    form.append('nivel', String(nivel))

    const response = await fetch(`${API_URL}/api/analyze`, {
        method: 'POST',
        headers: { Authorization: await getAuthHeader() },
        body: form,
    })

    if (!response.ok) {
        const text = await response.text()
        try {
            const error = JSON.parse(text)
            throw new Error(error.description || error.message || 'Error del servidor')
        } catch (err) {
            if (err instanceof SyntaxError) {
                throw new Error(`Error del servidor (${response.status}). Comprueba que el vídeo es correcto.`)
            }
            throw err
        }
    }

    return response.json()
}

// ===================
// Firestore — perfil de usuario
// ===================

export interface UserProfile {
    nombre:         string
    sexo:           string
    mano_dominante: string
    altura:         number
    nivel:          number
}

export async function getUserProfile(uid: string): Promise<UserProfile | null> {
    const { doc, getDoc } = await import('firebase/firestore')
    const snap = await getDoc(doc(db, 'users', uid))
    return snap.exists() ? snap.data() as UserProfile : null
}

// ===================
// Firestore — guardar análisis
// ===================

export async function saveAnalysis(
    uid:      string,
    filename: string,
    result:   AnalysisResult
): Promise<string> {
    const docRef = await addDoc(collection(db, 'analyses'), {
        uid,
        filename,
        custom_name: filename,
        score:       result.score,
        grade:       result.grade,
        stance:      result.stance,
        effect:      result.effect,
        nivel:       result.nivel ?? 5,
        breakdown:   result.breakdown,
        created_at:  serverTimestamp(),
    })
    return docRef.id
}

// ===================
// Firestore — obtener historial del usuario
// ===================

// ===================
// Firestore — colecciones
// ===================

export interface UserCollection {
    id:           string
    uid:          string
    name:         string
    analysis_ids: string[]
    created_at:   string
}

export async function getUserCollections(uid: string): Promise<UserCollection[]> {
    const q = query(collection(db, 'collections'), where('uid', '==', uid))
    const snapshot = await getDocs(q)
    return snapshot.docs.map(d => ({
        id: d.id,
        ...d.data(),
        created_at: d.data().created_at?.toDate().toISOString() ?? '',
    })) as UserCollection[]
}

export async function createCollection(uid: string, name: string): Promise<string> {
    const ref = await addDoc(collection(db, 'collections'), {
        uid, name, analysis_ids: [], created_at: serverTimestamp(),
    })
    return ref.id
}

export async function renameCollection(collectionId: string, name: string): Promise<void> {
    await updateDoc(doc(db, 'collections', collectionId), { name })
}

export async function deleteCollection(collectionId: string): Promise<void> {
    await deleteDoc(doc(db, 'collections', collectionId))
}

export async function addAnalysisToCollection(collectionId: string, analysisId: string): Promise<void> {
    await updateDoc(doc(db, 'collections', collectionId), { analysis_ids: arrayUnion(analysisId) })
}

export async function removeAnalysisFromCollection(collectionId: string, analysisId: string): Promise<void> {
    await updateDoc(doc(db, 'collections', collectionId), { analysis_ids: arrayRemove(analysisId) })
}

// ===================
// Firestore — editar / eliminar análisis
// ===================

export async function deleteAnalysis(uid: string, analysisId: string): Promise<void> {
    await deleteDoc(doc(db, 'analyses', analysisId))
    const cols = await getUserCollections(uid)
    await Promise.all(
        cols
            .filter(c => c.analysis_ids.includes(analysisId))
            .map(c => updateDoc(doc(db, 'collections', c.id), { analysis_ids: arrayRemove(analysisId) }))
    )
}

export async function renameAnalysis(analysisId: string, newName: string): Promise<void> {
    await updateDoc(doc(db, 'analyses', analysisId), { custom_name: newName })
}

// ===================
// Firestore — obtener historial del usuario
// ===================

export async function getUserAnalyses(uid: string): Promise<SavedAnalysis[]> {
    const q = query(collection(db, 'analyses'), where('uid', '==', uid))
    const snapshot = await getDocs(q)

    return snapshot.docs
        .map(doc => ({
            id: doc.id,
            ...doc.data(),
            created_at: doc.data().created_at?.toDate().toISOString() ?? '',
        })) as SavedAnalysis[]
}
