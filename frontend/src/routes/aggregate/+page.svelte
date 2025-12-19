<script lang="ts">
	import AuthGuard from '$lib/components/AuthGuard.svelte'

	// Aggregate page - admin only
</script>

<svelte:head>
	<title>Агрегация | TenderHack</title>
</svelte:head>

<AuthGuard requireAuth requireAdmin>
	<main>
		<!-- Aggregate content -->
	</main>
</AuthGuard>
