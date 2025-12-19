import { writable, derived } from 'svelte/store'

interface JwtPayload {
	sub: string // user id
	login: string
	is_admin: boolean
	exp?: number
	iat?: number
}

interface User {
	id: string
	login: string
	isAdmin: boolean
}

function parseJwt(token: string): JwtPayload | null {
	try {
		const base64Url = token.split('.')[1]
		const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/')
		const jsonPayload = decodeURIComponent(
			atob(base64)
				.split('')
				.map(c => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
				.join('')
		)
		return JSON.parse(jsonPayload)
	} catch {
		return null
	}
}

function isTokenExpired(payload: JwtPayload): boolean {
	if (!payload.exp) return false
	return Date.now() >= payload.exp * 1000
}

function getUserFromToken(token: string): User | null {
	const payload = parseJwt(token)
	if (!payload || isTokenExpired(payload)) {
		return null
	}
	return {
		id: payload.sub,
		login: payload.login,
		isAdmin: payload.is_admin,
	}
}

function createAuthStore() {
	const { subscribe, set, update } = writable<{
		token: string | null
		user: User | null
		isLoading: boolean
	}>({
		token: null,
		user: null,
		isLoading: true,
	})

	return {
		subscribe,
		setToken: (token: string | null) => {
			if (token) {
				const user = getUserFromToken(token)
				if (user) {
					localStorage.setItem('token', token)
					update(state => ({ ...state, token, user }))
				} else {
					// Invalid or expired token
					localStorage.removeItem('token')
					update(state => ({ ...state, token: null, user: null }))
				}
			} else {
				localStorage.removeItem('token')
				update(state => ({ ...state, token: null, user: null }))
			}
		},
		setLoading: (isLoading: boolean) => {
			update(state => ({ ...state, isLoading }))
		},
		logout: () => {
			localStorage.removeItem('token')
			set({ token: null, user: null, isLoading: false })
		},
		init: () => {
			if (typeof window !== 'undefined') {
				const token = localStorage.getItem('token')
				if (token) {
					const user = getUserFromToken(token)
					if (user) {
						update(state => ({ ...state, token, user, isLoading: false }))
					} else {
						// Token expired or invalid
						localStorage.removeItem('token')
						update(state => ({
							...state,
							token: null,
							user: null,
							isLoading: false,
						}))
					}
				} else {
					update(state => ({ ...state, isLoading: false }))
				}
			}
		},
	}
}

export const auth = createAuthStore()
export const isAuthenticated = derived(auth, $auth => !!$auth.token)
// TODO: ПЕРЕДЕЛАТЬ НА ПРОДЕ
export const isAdmin = derived(auth, $auth => $auth.user?.isAdmin ?? false)
