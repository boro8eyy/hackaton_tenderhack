import { fetchApi } from './index'
import type { Ste } from './ste'

// =============================================================================
// Types (based on backend schemas)
// =============================================================================

export interface Card {
	id: number
	name?: string | null
	stes: Ste[]
}

export interface CardCreateRequest {
	name?: string
	ste_ids?: number[]
}

export interface CardUpdateRequest {
	name?: string
}

// Legacy types for card detail page (can be removed later)
export interface CardFeature {
	name: string
	value: string
}

export interface CardDetail {
	id: string
	card_id: string
	title: string
	category_id: string
	category_name: string
	image_url: string | null
	features: CardFeature[]
	model: string | null
	country: string | null
	manufacturer: string | null
}

// =============================================================================

// Admin endpoints
export async function getCardList(
	query?: string,
	categoryIds?: number[]
): Promise<Card[]> {
	const params = new URLSearchParams()
	if (query) params.append('q', query)
	if (categoryIds && categoryIds.length > 0) {
		params.append('category_id', categoryIds[0].toString())
	}
	const queryString = params.toString()
	return fetchApi<Card[]>(
		`/api/admin/card/${queryString ? '?' + queryString : ''}`
	)
}

export async function createCard(data: CardCreateRequest): Promise<Card> {
	return fetchApi<Card>('/api/admin/card/', {
		method: 'POST',
		body: JSON.stringify(data),
	})
}

export async function getCardById(id: number): Promise<Card> {
	return fetchApi<Card>(`/api/admin/card/${id}`)
}

export async function updateCard(
	id: number,
	data: CardUpdateRequest
): Promise<Card> {
	return fetchApi<Card>(`/api/admin/card/${id}`, {
		method: 'PATCH',
		body: JSON.stringify(data),
	})
}

export async function deleteCard(id: number): Promise<{ msg: string }> {
	return fetchApi<{ msg: string }>(`/api/admin/card/${id}`, {
		method: 'DELETE',
	})
}

// Public endpoint - returns STE data for card/ste relation
export async function getCardSteRelation(
	cardId: number,
	steId: number
): Promise<Ste> {
	return fetchApi<Ste>(`/api/card/${cardId}/${steId}`)
}
