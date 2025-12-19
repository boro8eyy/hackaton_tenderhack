import { fetchApi } from './index'

export interface Category {
	id: number
	name: string
}

export async function getCategories(): Promise<Category[]> {
	return fetchApi<Category[]>('/api/categories')
}
