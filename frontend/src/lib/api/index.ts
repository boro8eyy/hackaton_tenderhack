// API client configuration and methods
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// =============================================================================
// Error Handling
// =============================================================================
export class ApiError extends Error {
	constructor(
		public status: number,
		public statusText: string,
		public data?: ApiErrorResponse | null
	) {
		super(data?.detail || data?.message || `API Error: ${status} ${statusText}`)
		this.name = 'ApiError'
	}
}

export interface ApiErrorResponse {
	message?: string
	errors?: Record<string, string[]>
	detail?: string
}

async function handleApiError(response: Response): Promise<never> {
	let errorData: ApiErrorResponse | null = null
	try {
		errorData = await response.json()
	} catch {
		// Response body is not JSON
	}
	throw new ApiError(response.status, response.statusText, errorData)
}
// =============================================================================

function getAuthHeader(): Record<string, string> {
	if (typeof window === 'undefined') return {}
	const token = localStorage.getItem('token')
	return token ? { Authorization: `Bearer ${token}` } : {}
}

export async function fetchApi<T>(
	endpoint: string,
	options?: RequestInit
): Promise<T> {
	const response = await fetch(`${API_BASE_URL}${endpoint}`, {
		headers: {
			'Content-Type': 'application/json',
			...getAuthHeader(),
			...options?.headers,
		},
		...options,
	})

	if (!response.ok) {
		await handleApiError(response)
	}

	return response.json()
}

export { API_BASE_URL, handleApiError }

// Re-export all API modules
export * from './auth'
export * from './ste'
export * from './card'
export * from './search'
export * from './aggregation'
export * from './categories'
