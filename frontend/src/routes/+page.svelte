<script lang="ts">
	let count = $state(0)

	function increment() {
		count++
	}
</script>

<svelte:head>
	<title>TenderHack - Главная</title>
</svelte:head>

<main>
	<h1>TenderHack</h1>
	<p>Добро пожаловать в проект!</p>

	<div class="counter">
		<button onclick={increment}>
			Счётчик: {count}
		</button>
	</div>
</main>

<style>
	main {
		flex: 1;
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		padding: 2rem;
	}

	h1 {
		font-size: 2.5rem;
		margin-bottom: 1rem;
		color: var(--color-primary);
	}

	p {
		color: var(--color-text-light);
		margin-bottom: 2rem;
	}

	.counter {
		margin-top: 1rem;
	}

	button {
		padding: 0.75rem 1.5rem;
		font-size: 1rem;
		background-color: var(--color-primary);
		color: white;
		border: none;
		border-radius: 0.5rem;
		transition: background-color 0.2s;
	}

	button:hover {
		background-color: var(--color-secondary);
	}
</style>
