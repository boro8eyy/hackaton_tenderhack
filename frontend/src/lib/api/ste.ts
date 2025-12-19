import { fetchApi, API_BASE_URL, handleApiError } from './index'

// =============================================================================
// Types (based on backend schemas)
// =============================================================================
export interface SteCharacteristics {
	[key: string]: string | number | boolean
}

export interface Ste {
	id: number
	name: string
	category_id: number | null
	characteristics: SteCharacteristics
	card_id?: number | null
	// Extended fields from import
	external_id?: number | null
	image_url?: string | null
	model_name?: string | null
	country_of_origin?: string | null
	manufacturer?: string | null
	category_name?: string | null
}

export interface SteCreateRequest {
	name: string
	description?: string
	category_id: number
	characteristics?: SteCharacteristics
}

export interface SteUpdateRequest {
	name?: string
	description?: string
	characteristics?: SteCharacteristics
	card_id?: number | null
}
// =============================================================================

export async function getSteList(
	query?: string,
	categoryIds?: number[],
	limit: number = 100,
	skip: number = 0
): Promise<Ste[]> {
	const params = new URLSearchParams()
	if (query) params.append('q', query)
	if (categoryIds && categoryIds.length > 0) {
		// API принимает только один category_id, берём первый
		params.append('category_id', categoryIds[0].toString())
	}
	params.append('limit', limit.toString())
	params.append('skip', skip.toString())
	const queryString = params.toString()
	return fetchApi<Ste[]>(
		`/api/admin/ste${queryString ? '?' + queryString : ''}`
	)
}

/**
 * Загружает все СТЕ, используя пагинацию
 */
export async function getAllStes(
	query?: string,
	categoryIds?: number[]
): Promise<Ste[]> {
	const allStes: Ste[] = []
	const batchSize = 500
	let skip = 0
	let hasMore = true

	while (hasMore) {
		const batch = await getSteList(query, categoryIds, batchSize, skip)
		allStes.push(...batch)
		if (batch.length < batchSize) {
			hasMore = false
		} else {
			skip += batchSize
		}
	}

	return allStes
}

export async function createSte(data: SteCreateRequest): Promise<Ste> {
	return fetchApi<Ste>('/api/admin/ste', {
		method: 'POST',
		body: JSON.stringify(data),
	})
}

export async function getSteById(id: number): Promise<Ste> {
	return fetchApi<Ste>(`/api/admin/ste/${id}`)
}

export async function updateSte(
	id: number,
	data: SteUpdateRequest
): Promise<Ste> {
	return fetchApi<Ste>(`/api/admin/ste/${id}`, {
		method: 'PATCH',
		body: JSON.stringify(data),
	})
}

export async function deleteSte(id: number): Promise<{ msg: string }> {
	return fetchApi<{ msg: string }>(`/api/admin/ste/${id}`, {
		method: 'DELETE',
	})
}

const ALLOWED_FILE_TYPES = [
	'text/csv',
	'application/vnd.ms-excel',
	'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
]

const ALLOWED_EXTENSIONS = ['.csv', '.xlsx', '.xls']

function isValidFileType(file: File): boolean {
	const extension = file.name.toLowerCase().slice(file.name.lastIndexOf('.'))
	return (
		ALLOWED_FILE_TYPES.includes(file.type) ||
		ALLOWED_EXTENSIONS.includes(extension)
	)
}

export async function uploadSte(file: File): Promise<unknown> {
	// Validate file type
	if (!isValidFileType(file)) {
		throw new Error('Неверный формат файла. Допустимые форматы: .csv, .xlsx')
	}

	// Note: For file uploads, we need to use FormData and remove Content-Type header
	// so the browser can set it with the correct boundary
	const formData = new FormData()
	formData.append('file', file)

	const token =
		typeof window !== 'undefined' ? localStorage.getItem('token') : null
	const headers: Record<string, string> = {}
	if (token) {
		headers['Authorization'] = `Bearer ${token}`
	}

	const response = await fetch(`${API_BASE_URL}/api/admin/ste/upload`, {
		method: 'POST',
		headers,
		body: formData,
	})

	if (!response.ok) {
		await handleApiError(response)
	}

	return response.json()
}
