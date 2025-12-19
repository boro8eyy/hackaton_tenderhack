<script lang="ts">
	import { goto } from '$app/navigation'
	import { onMount } from 'svelte'

	onMount(() => {
		goto('/search', { replaceState: true })
	})
</script>

<div class="loading">
	<p>Перенаправление...</p>
</div>

<style>
	.loading {
		display: flex;
		align-items: center;
		justify-content: center;
		min-height: 100vh;
		font-family: 'Golos Text', sans-serif;
		color: #666;
	}
</style>
