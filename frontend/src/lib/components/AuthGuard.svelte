<script lang="ts">
	import { goto } from '$app/navigation'
	import { auth, isAdmin, isAuthenticated } from '$lib/stores/auth'
	import type { Snippet } from 'svelte'

	interface Props {
		requireAuth?: boolean
		requireAdmin?: boolean
		children: Snippet
	}

	let { requireAuth = false, requireAdmin = false, children }: Props = $props()

	$effect(() => {
		if ($auth.isLoading) return

		if (requireAuth && !$isAuthenticated) {
			goto('/login')
			return
		}

		if (requireAdmin && !$isAdmin) {
			goto('/catalog')
			return
		}
	})
</script>

{#if $auth.isLoading}
	<div class="loading">Загрузка...</div>
{:else if requireAdmin && !$isAdmin}
	<div class="loading">Доступ запрещён</div>
{:else if requireAuth && !$isAuthenticated}
	<div class="loading">Требуется авторизация</div>
{:else}
	{@render children()}
{/if}

<style>
	.loading {
		display: flex;
		align-items: center;
		justify-content: center;
		min-height: 100vh;
		font-size: 1.25rem;
		color: var(--color-text-light);
	}
</style>
