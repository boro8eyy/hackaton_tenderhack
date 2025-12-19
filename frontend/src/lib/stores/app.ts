import { writable } from 'svelte/store'

// Global application state
export const isLoading = writable<boolean>(false)
export const error = writable<string | null>(null)
