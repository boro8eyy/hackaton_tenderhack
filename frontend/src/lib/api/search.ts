import { fetchApi } from './index'
import type { Ste } from './ste'

// Интерфейс пагинированного ответа
export interface PaginatedResponse<T> {
	items: T[]
	total: number
	page: number
	per_page: number
	total_pages: number
}

export interface SearchParams {
	query: string
	exact?: boolean
	page?: number
	per_page?: number
	category_id?: number | null
}

// Поиск возвращает пагинированный ответ
export async function search(
	params: SearchParams
): Promise<PaginatedResponse<Ste>> {
	const urlParams = new URLSearchParams()
	urlParams.set('query', params.query)
	if (params.exact) urlParams.set('exact', 'true')
	if (params.page) urlParams.set('page', params.page.toString())
	if (params.per_page) urlParams.set('per_page', params.per_page.toString())
	if (params.category_id !== undefined && params.category_id !== null) {
		urlParams.set('category_id', params.category_id.toString())
	}
	return fetchApi<PaginatedResponse<Ste>>(`/api/search?${urlParams.toString()}`)
}
