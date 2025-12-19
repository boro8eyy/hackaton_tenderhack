<script lang="ts">
	import { page } from '$app/stores'
	import { getCardById, type Card } from '$lib/api/card'
	import AuthGuard from '$lib/components/AuthGuard.svelte'
	import Header from '$lib/components/Header.svelte'
	import { onMount } from 'svelte'

	let id = $derived($page.params.id ?? '0')
	let cardId = $derived(parseInt(id))

	// Data state
	let card = $state<Card | null>(null)
	let loading = $state(true)
	let error = $state<string | null>(null)

	onMount(async () => {
		await loadCard()
	})

	async function loadCard() {
		loading = true
		error = null
		try {
			card = await getCardById(cardId)
		} catch (e) {
			console.error('Failed to load card:', e)
			error = e instanceof Error ? e.message : 'Ошибка загрузки карточки'
		} finally {
			loading = false
		}
	}
</script>

<svelte:head>
	<title>{card?.name || `Карточка #${id}`} | TenderHack</title>
</svelte:head>

<AuthGuard requireAdmin>
	<div class="page-wrapper">
		<Header />

		<main class="content">
			<div class="page-header">
				<a href="/card" class="back-link">
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
				{:else if card}
					<div class="title-row">
						<h1 class="page-title">
							{card.name || `Карточка #${card.id}`}
						</h1>
						<a href="/card/{card.id}/edit" class="btn-edit">
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
					<a href="/card" class="btn-secondary">Вернуться к списку</a>
				</div>
			{:else if card}
				<div class="card-info">
					<div class="info-section">
						<h2 class="section-title">Информация о карточке</h2>
						<div class="info-grid">
							<div class="info-item">
								<span class="info-label">ID карточки</span>
								<span class="info-value">{card.id}</span>
							</div>
							<div class="info-item">
								<span class="info-label">Название</span>
								<span class="info-value">{card.name || '—'}</span>
							</div>
							<div class="info-item">
								<span class="info-label">Количество СТЕ</span>
								<span class="info-value">{card.stes?.length || 0}</span>
							</div>
						</div>
					</div>

					<div class="info-section">
						<h2 class="section-title">
							СТЕ в карточке
							<span class="section-count">({card.stes?.length || 0})</span>
						</h2>

						{#if card.stes && card.stes.length > 0}
							<div class="ste-grid">
								{#each card.stes as ste}
									<div class="ste-card">
										<div class="ste-image-container">
											{#if ste.image_url}
												<img
													src={ste.image_url}
													alt={ste.name}
													class="ste-image"
												/>
											{:else}
												<div class="ste-no-image">
													<svg
														width="40"
														height="40"
														viewBox="0 0 24 24"
														fill="none"
													>
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
												</div>
											{/if}
										</div>
										<div class="ste-content">
											<h3 class="ste-name">{ste.name}</h3>
											<div class="ste-meta">
												{#if ste.model_name}
													<span class="ste-meta-item">
														<span class="meta-label">Модель:</span>
														{ste.model_name}
													</span>
												{/if}
												{#if ste.manufacturer}
													<span class="ste-meta-item">
														<span class="meta-label">Производитель:</span>
														{ste.manufacturer}
													</span>
												{/if}
												{#if ste.country_of_origin}
													<span class="ste-meta-item">
														<span class="meta-label">Страна:</span>
														{ste.country_of_origin}
													</span>
												{/if}
												{#if ste.category_name}
													<span class="ste-meta-item">
														<span class="meta-label">Категория:</span>
														{ste.category_name}
													</span>
												{/if}
											</div>
											{#if ste.characteristics && Object.keys(ste.characteristics).length > 0}
												<div class="ste-characteristics">
													<h4 class="characteristics-title">Характеристики:</h4>
													<div class="characteristics-list">
														{#each Object.entries(ste.characteristics).slice(0, 6) as [key, value]}
															<div class="characteristic-item">
																<span class="char-key">{key}:</span>
																<span class="char-value">{value}</span>
															</div>
														{/each}
														{#if Object.keys(ste.characteristics).length > 6}
															<div class="characteristics-more">
																+{Object.keys(ste.characteristics).length - 6} характеристик
															</div>
														{/if}
													</div>
												</div>
											{/if}
										</div>
									</div>
								{/each}
							</div>
						{:else}
							<div class="empty-state">
								<p>В этой карточке пока нет СТЕ</p>
								<a href="/card/{card.id}/edit" class="btn-secondary">
									Добавить СТЕ
								</a>
							</div>
						{/if}
					</div>
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

	.card-info {
		display: flex;
		flex-direction: column;
		gap: 24px;
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

	.section-count {
		font-weight: 400;
		color: #666;
	}

	.info-grid {
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
		gap: 24px;
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

	.ste-grid {
		display: flex;
		flex-direction: column;
		gap: 16px;
	}

	.ste-card {
		display: flex;
		gap: 20px;
		padding: 20px;
		background: #fafafa;
		border-radius: 10px;
		border: 1px solid #e5e5e5;
	}

	.ste-image-container {
		flex-shrink: 0;
		width: 120px;
		height: 120px;
		border-radius: 8px;
		overflow: hidden;
		background: #f0f0f0;
	}

	.ste-image {
		width: 100%;
		height: 100%;
		object-fit: cover;
	}

	.ste-no-image {
		width: 100%;
		height: 100%;
		display: flex;
		align-items: center;
		justify-content: center;
		background: #f5f5f5;
	}

	.ste-content {
		flex: 1;
		min-width: 0;
	}

	.ste-name {
		font-size: 16px;
		font-weight: 600;
		color: #333;
		margin: 0 0 8px;
	}

	.ste-meta {
		display: flex;
		flex-wrap: wrap;
		gap: 16px;
		margin-bottom: 12px;
	}

	.ste-meta-item {
		font-size: 13px;
		color: #666;
	}

	.meta-label {
		color: #999;
	}

	.ste-characteristics {
		margin-top: 12px;
		padding-top: 12px;
		border-top: 1px solid #e5e5e5;
	}

	.characteristics-title {
		font-size: 13px;
		font-weight: 500;
		color: #666;
		margin: 0 0 8px;
	}

	.characteristics-list {
		display: flex;
		flex-wrap: wrap;
		gap: 8px 16px;
	}

	.characteristic-item {
		font-size: 13px;
		color: #333;
	}

	.char-key {
		color: #666;
	}

	.char-value {
		font-weight: 500;
	}

	.characteristics-more {
		font-size: 13px;
		color: #999;
		font-style: italic;
	}

	.empty-state {
		text-align: center;
		padding: 40px;
		background: #fafafa;
		border-radius: 10px;
	}

	.empty-state p {
		color: #666;
		margin-bottom: 16px;
	}

	@media (max-width: 1200px) {
		.content {
			padding: 24px 40px 40px;
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

		.info-section {
			padding: 20px;
		}

		.ste-card {
			flex-direction: column;
		}

		.ste-image-container {
			width: 100%;
			height: 200px;
		}
	}
</style>
