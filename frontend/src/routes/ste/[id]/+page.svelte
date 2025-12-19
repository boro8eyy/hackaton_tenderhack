<script lang="ts">
	import { page } from '$app/stores'
	import { getSteById, type Ste } from '$lib/api/ste'
	import AuthGuard from '$lib/components/AuthGuard.svelte'
	import Header from '$lib/components/Header.svelte'
	import { onMount } from 'svelte'

	let id = $derived($page.params.id ?? '0')
	let steId = $derived(parseInt(id))

	// Data state
	let ste = $state<Ste | null>(null)
	let loading = $state(true)
	let error = $state<string | null>(null)

	onMount(async () => {
		await loadSte()
	})

	async function loadSte() {
		loading = true
		error = null
		try {
			ste = await getSteById(steId)
		} catch (e) {
			console.error('Failed to load STE:', e)
			error = e instanceof Error ? e.message : 'Ошибка загрузки СТЕ'
		} finally {
			loading = false
		}
	}
</script>

<svelte:head>
	<title>{ste?.name || `СТЕ #${id}`} | TenderHack</title>
</svelte:head>

<AuthGuard requireAdmin>
	<div class="page-wrapper">
		<Header />

		<main class="content">
			<div class="page-header">
				<a href="/ste" class="back-link">
					<svg width="20" height="20" viewBox="0 0 20 20" fill="none">
						<path
							d="M12.5 15L7.5 10L12.5 5"
							stroke="currentColor"
							stroke-width="1.5"
							stroke-linecap="round"
							stroke-linejoin="round"
						/>
					</svg>
					Назад к списку
				</a>

				{#if loading}
					<h1 class="page-title">Загрузка...</h1>
				{:else if error}
					<h1 class="page-title">Ошибка</h1>
				{:else if ste}
					<div class="title-row">
						<h1 class="page-title">{ste.name}</h1>
						<a href="/ste/{ste.id}/edit" class="btn-edit">
							<svg width="18" height="18" viewBox="0 0 18 18" fill="none">
								<path
									d="M12.75 2.25L15.75 5.25M1.5 16.5L2.25 13.125L13.5 1.875C13.6989 1.67606 13.9348 1.51778 14.1947 1.40915C14.4546 1.30052 14.7333 1.24371 15.0149 1.24197C15.2965 1.24022 15.5759 1.29357 15.8372 1.39898C16.0984 1.50439 16.3362 1.6597 16.5377 1.85723C16.7392 2.05475 16.8994 2.28955 17.0099 2.54853C17.1204 2.80751 17.1788 3.08543 17.1819 3.36694C17.185 3.64845 17.1328 3.9277 17.0281 4.18904C16.9234 4.45038 16.7686 4.68852 16.5729 4.89L5.25 16.125L1.5 16.5Z"
									stroke="currentColor"
									stroke-width="1.5"
									stroke-linecap="round"
									stroke-linejoin="round"
								/>
							</svg>
							Редактировать
						</a>
					</div>
				{/if}
			</div>

			{#if loading}
				<div class="loading-container">
					<p>Загрузка данных...</p>
				</div>
			{:else if error}
				<div class="error-container">
					<p>{error}</p>
					<a href="/ste" class="btn-secondary">Вернуться к списку</a>
				</div>
			{:else if ste}
				<div class="ste-detail">
					<div class="detail-grid">
						<!-- Изображение -->
						<div class="image-section">
							{#if ste.image_url}
								<img src={ste.image_url} alt={ste.name} class="ste-image" />
							{:else}
								<div class="no-image">
									<svg width="60" height="60" viewBox="0 0 24 24" fill="none">
										<rect
											x="3"
											y="3"
											width="18"
											height="18"
											rx="2"
											stroke="#ccc"
											stroke-width="1.5"
										/>
										<circle
											cx="8.5"
											cy="8.5"
											r="1.5"
											stroke="#ccc"
											stroke-width="1.5"
										/>
										<path
											d="M3 16L8 11L13 16"
											stroke="#ccc"
											stroke-width="1.5"
											stroke-linecap="round"
										/>
										<path
											d="M13 14L16 11L21 16"
											stroke="#ccc"
											stroke-width="1.5"
											stroke-linecap="round"
										/>
									</svg>
									<span>Нет изображения</span>
								</div>
							{/if}
						</div>

						<!-- Основная информация -->
						<div class="info-section">
							<h2 class="section-title">Основная информация</h2>
							<div class="info-grid">
								<div class="info-item">
									<span class="info-label">ID СТЕ</span>
									<span class="info-value">{ste.id}</span>
								</div>
								{#if ste.external_id}
									<div class="info-item">
										<span class="info-label">Внешний ID</span>
										<span class="info-value">{ste.external_id}</span>
									</div>
								{/if}
								<div class="info-item">
									<span class="info-label">Название</span>
									<span class="info-value">{ste.name}</span>
								</div>
								{#if ste.model_name}
									<div class="info-item">
										<span class="info-label">Модель</span>
										<span class="info-value">{ste.model_name}</span>
									</div>
								{/if}
								{#if ste.manufacturer}
									<div class="info-item">
										<span class="info-label">Производитель</span>
										<span class="info-value">{ste.manufacturer}</span>
									</div>
								{/if}
								{#if ste.country_of_origin}
									<div class="info-item">
										<span class="info-label">Страна происхождения</span>
										<span class="info-value">{ste.country_of_origin}</span>
									</div>
								{/if}
								{#if ste.category_name}
									<div class="info-item">
										<span class="info-label">Категория</span>
										<span class="info-value">{ste.category_name}</span>
									</div>
								{/if}
								<div class="info-item">
									<span class="info-label">ID Карточки</span>
									<span class="info-value">
										{#if ste.card_id}
											<a href="/card/{ste.card_id}" class="link"
												>{ste.card_id}</a
											>
										{:else}
											<span class="no-value">Не привязан</span>
										{/if}
									</span>
								</div>
							</div>
						</div>
					</div>

					<!-- Характеристики -->
					{#if ste.characteristics && Object.keys(ste.characteristics).length > 0}
						<div class="characteristics-section">
							<h2 class="section-title">Характеристики</h2>
							<div class="characteristics-grid">
								{#each Object.entries(ste.characteristics) as [key, value]}
									<div class="characteristic-item">
										<span class="char-key">{key}</span>
										<span class="char-value">{value}</span>
									</div>
								{/each}
							</div>
						</div>
					{/if}
				</div>
			{/if}
		</main>
	</div>
</AuthGuard>

<style>
	.page-wrapper {
		background-color: #f2f2f2;
		min-height: 100vh;
	}

	.content {
		padding: 24px 160px 40px;
		max-width: 1440px;
		margin: 0 auto;
	}

	.page-header {
		margin-bottom: 24px;
	}

	.back-link {
		display: inline-flex;
		align-items: center;
		gap: 8px;
		color: #666;
		text-decoration: none;
		font-size: 14px;
		margin-bottom: 16px;
	}

	.back-link:hover {
		color: #cd1f15;
	}

	.title-row {
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 16px;
	}

	.page-title {
		font-size: 32px;
		font-weight: 600;
		color: #333;
		margin: 0;
	}

	.btn-edit {
		display: flex;
		align-items: center;
		gap: 8px;
		height: 40px;
		padding: 0 20px;
		background: white;
		border: none;
		border-radius: 8px;
		font-family: inherit;
		font-size: 14px;
		color: #333;
		text-decoration: none;
		cursor: pointer;
	}

	.btn-edit:hover {
		background: #f5f5f5;
	}

	.loading-container,
	.error-container {
		background: white;
		border-radius: 12px;
		padding: 60px 40px;
		text-align: center;
	}

	.error-container p {
		color: #cd1f15;
		margin-bottom: 20px;
	}

	.btn-secondary {
		display: inline-flex;
		align-items: center;
		gap: 8px;
		height: 40px;
		padding: 0 20px;
		background: white;
		border: 1px solid #ccc;
		border-radius: 8px;
		font-family: inherit;
		font-size: 14px;
		color: #333;
		text-decoration: none;
		cursor: pointer;
	}

	.btn-secondary:hover {
		background: #f5f5f5;
	}

	.ste-detail {
		display: flex;
		flex-direction: column;
		gap: 24px;
	}

	.detail-grid {
		display: grid;
		grid-template-columns: 300px 1fr;
		gap: 24px;
	}

	.image-section {
		background: white;
		border-radius: 12px;
		overflow: hidden;
	}

	.ste-image {
		width: 100%;
		aspect-ratio: 1;
		object-fit: cover;
	}

	.no-image {
		width: 100%;
		aspect-ratio: 1;
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		gap: 12px;
		background: #f5f5f5;
		color: #999;
		font-size: 14px;
	}

	.info-section {
		background: white;
		border-radius: 12px;
		padding: 32px;
	}

	.section-title {
		font-size: 20px;
		font-weight: 600;
		color: #333;
		margin: 0 0 20px;
	}

	.info-grid {
		display: grid;
		grid-template-columns: repeat(2, 1fr);
		gap: 20px;
	}

	.info-item {
		display: flex;
		flex-direction: column;
		gap: 4px;
	}

	.info-label {
		font-size: 13px;
		color: #666;
	}

	.info-value {
		font-size: 16px;
		font-weight: 500;
		color: #333;
	}

	.link {
		color: #cd1f15;
		text-decoration: none;
	}

	.link:hover {
		text-decoration: underline;
	}

	.no-value {
		color: #999;
		font-weight: 400;
	}

	.characteristics-section {
		background: white;
		border-radius: 12px;
		padding: 32px;
	}

	.characteristics-grid {
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
		gap: 16px;
	}

	.characteristic-item {
		display: flex;
		justify-content: space-between;
		gap: 16px;
		padding: 12px 16px;
		background: #fafafa;
		border-radius: 8px;
	}

	.char-key {
		font-size: 14px;
		color: #666;
	}

	.char-value {
		font-size: 14px;
		font-weight: 500;
		color: #333;
		text-align: right;
	}

	@media (max-width: 1200px) {
		.content {
			padding: 24px 40px 40px;
		}
	}

	@media (max-width: 900px) {
		.detail-grid {
			grid-template-columns: 1fr;
		}

		.image-section {
			max-width: 400px;
		}
	}

	@media (max-width: 768px) {
		.content {
			padding: 16px;
		}

		.title-row {
			flex-direction: column;
			align-items: flex-start;
		}

		.info-section,
		.characteristics-section {
			padding: 20px;
		}

		.info-grid {
			grid-template-columns: 1fr;
		}

		.characteristics-grid {
			grid-template-columns: 1fr;
		}
	}
</style>
