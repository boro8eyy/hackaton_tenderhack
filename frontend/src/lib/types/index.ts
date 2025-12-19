// Types and interfaces for the application
export interface User {
	id: string
	name: string
	email: string
}

export interface ApiResponse<T> {
	data: T
	success: boolean
	message?: string
}
