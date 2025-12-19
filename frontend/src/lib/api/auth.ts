import { fetchApi } from './index'

// =============================================================================
// Types (customize based on your backend response)
// =============================================================================
// export interface LoginRequest {
// 	login: string
// 	password: string
// }
//
// export interface RegisterRequest {
// 	login: string
// 	password: string
// 	// email?: string
// }
//
// export interface AuthResponse {
// 	access_token: string
// 	token_type: string
// }
// =============================================================================

export async function login(data: unknown): Promise<unknown> {
	return fetchApi('/api/auth/login', {
		method: 'POST',
		body: JSON.stringify(data),
	})
}

export async function register(data: unknown): Promise<unknown> {
	return fetchApi('/api/auth/register', {
		method: 'POST',
		body: JSON.stringify(data),
	})
}
