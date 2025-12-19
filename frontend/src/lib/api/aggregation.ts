import { fetchApi } from './index'

// =============================================================================
// Types
// =============================================================================
export interface ReaggregateRequest {
	ste_ids: number[]
}

export interface ReaggregateResponse {
	status: string
	total: number
	updated: number
}
// =============================================================================

/**
 * Запустить реагрегацию для указанных STE
 */
export async function reaggregateStes(
	steIds: number[]
): Promise<ReaggregateResponse> {
	return fetchApi<ReaggregateResponse>('/api/admin/reaggregate', {
		method: 'POST',
		body: JSON.stringify({ ste_ids: steIds }),
	})
}

/**
 * Запустить реагрегацию для всех STE
 */
export async function reaggregateAll(): Promise<ReaggregateResponse> {
	return fetchApi<ReaggregateResponse>('/api/admin/reaggregate/all', {
		method: 'POST',
	})
}
