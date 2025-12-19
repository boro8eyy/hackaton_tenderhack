<script lang="ts">
	import { auth } from '$lib/stores/auth'
	import { onMount } from 'svelte'
	import '../styles/global.css'

	let { children } = $props()

	onMount(() => {
		auth.init()
	})
</script>

<div class="app">
	{@render children()}
</div>

<style>
	.app {
		min-height: 100vh;
		display: flex;
		flex-direction: column;
	}
</style>
