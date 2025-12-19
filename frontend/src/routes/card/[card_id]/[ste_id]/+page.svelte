<script lang="ts">
	import { page } from '$app/stores'
	import { getCardById, getCardSteRelation, type Card } from '$lib/api/card'
	import { getSteById, type Ste } from '$lib/api/ste'
	import notFoundImage from '$lib/assets/not_found.png'
	import Header from '$lib/components/Header.svelte'
	import { isAdmin } from '$lib/stores/auth'
	import { onMount } from 'svelte'

	let cardId = $derived(parseInt($page.params.card_id ?? '0', 10))
	let steId = $derived(parseInt($page.params.ste_id ?? '0', 10))

	let ste = $state<Ste | null>(null)
	let card = $state<Card | null>(null)
	let loading = $state(true)
	let error = $state<string | null>(null)

	async function loadSte() {
		if (isNaN(steId)) {
			error = 'Неверные параметры страницы'
			loading = false
			return
		}
		loading = true
		error = null
		try {
			// Если card_id = 0, СТЕ не привязан к карточке - загружаем только СТЕ
			if (cardId === 0) {
				ste = await getSteById(steId)
				card = null
			} else {
				const [steData, cardData] = await Promise.all([
					getCardSteRelation(cardId, steId),
					getCardById(cardId).catch(() => null),
				])
				ste = steData
				card = cardData
			}
		} catch (e) {
			error = e instanceof Error ? e.message : 'Ошибка загрузки данных'
		} finally {
			loading = false
		}
	}

	function copyToClipboard(text: string) {
		navigator.clipboard.writeText(text)
	}

	// Преобразование characteristics в массив для отображения
	let features = $derived.by(() => {
		if (!ste?.characteristics) return []
		return Object.entries(ste.characteristics).map(([key, value]) => ({
			name: key,
			value: String(value),
		}))
	})

	onMount(() => {
		loadSte()
	})

	// Reload when params change
	$effect(() => {
		if (!isNaN(cardId) && !isNaN(steId)) {
			loadSte()
		}
	})
</script>

<svelte:head>
	<title>{ste?.name ?? 'Карточка СТЕ'} | TenderHack</title>
</svelte:head>

<div class="page-wrapper">
	<Header />

	<main class="content">
		{#if loading}
			<div class="loading">
				<p>Загрузка...</p>
			</div>
		{:else if error}
			<div class="error">
				<p>{error}</p>
				<button class="btn-primary" onclick={loadSte}>Повторить</button>
			</div>
		{:else if ste}
			<!-- Хлебные крошки + ID СТЕ -->
			<div class="top-row">
				<nav class="breadcrumbs">
					<a href="/catalog" class="breadcrumb-link">Товары</a>
					<span class="breadcrumb-separator">
						<svg width="20" height="20" viewBox="0 0 20 20" fill="none">
							<path
								d="M7.5 5L12.5 10L7.5 15"
								stroke="#A7A7AB"
								stroke-width="1.5"
								stroke-linecap="round"
								stroke-linejoin="round"
							/>
						</svg>
					</span>
					{#if ste.category_name}
						<a href="/search?category={ste.category_id}" class="breadcrumb-link"
							>{ste.category_name}</a
						>
						{#if cardId !== 0}
							<span class="breadcrumb-separator">
								<svg width="20" height="20" viewBox="0 0 20 20" fill="none">
									<path
										d="M7.5 5L12.5 10L7.5 15"
										stroke="#A7A7AB"
										stroke-width="1.5"
										stroke-linecap="round"
										stroke-linejoin="round"
									/>
								</svg>
							</span>
						{/if}
					{/if}
					{#if cardId !== 0}
						{#if $isAdmin}
							<a href="/card/{cardId}" class="breadcrumb-link"
								>{card?.name || `Карточка #${cardId}`}</a
							>
						{:else}
							<span class="breadcrumb-current"
								>{card?.name || `Карточка #${cardId}`}</span
							>
						{/if}
					{/if}
				</nav>

				<div class="ste-id-container">
					<span class="ste-id-text">ID СТЕ: {steId}</span>
					<button
						class="copy-btn"
						onclick={() => copyToClipboard(String(steId))}
						aria-label="Копировать ID"
					>
						<svg width="20" height="20" viewBox="0 0 20 20" fill="none">
							<rect
								x="6"
								y="6"
								width="11"
								height="11"
								rx="2"
								stroke="#76767A"
								stroke-width="1.5"
							/>
							<path
								d="M4 14V4C4 2.89543 4.89543 2 6 2H14"
								stroke="#76767A"
								stroke-width="1.5"
								stroke-linecap="round"
							/>
						</svg>
					</button>
				</div>
			</div>

			<!-- Основной блок -->
			<div class="card-main">
				<!-- Изображение -->
				<div class="card-image-container">
					<img
						src={ste.image_url ?? notFoundImage}
						alt={ste.name}
						class="card-image"
					/>
				</div>

				<!-- Информация -->
				<div class="card-info">
					<h1 class="card-title">{ste.name}</h1>
					<h2 class="section-title">Общие сведения</h2>

					<div class="info-table">
						{#if cardId !== 0}
							<div class="info-row">
								<span class="info-label">ID Карточки</span>
								<span class="info-line"></span>
								{#if $isAdmin}
									<a href="/card/{cardId}" class="info-value info-link"
										>{cardId}</a
									>
								{:else}
									<span class="info-value">{cardId}</span>
								{/if}
							</div>
						{/if}
						{#if ste.external_id}
							<div class="info-row">
								<span class="info-label">Внешний ID</span>
								<span class="info-line"></span>
								<span class="info-value">{ste.external_id}</span>
							</div>
						{/if}
						{#if ste.manufacturer}
							<div class="info-row">
								<span class="info-label">Производитель</span>
								<span class="info-line"></span>
								<span class="info-value">{ste.manufacturer}</span>
							</div>
						{/if}
						{#if ste.country_of_origin}
							<div class="info-row">
								<span class="info-label">Страна</span>
								<span class="info-line"></span>
								<span class="info-value">{ste.country_of_origin}</span>
							</div>
						{/if}
						{#if ste.model_name}
							<div class="info-row">
								<span class="info-label">Модель</span>
								<span class="info-line"></span>
								<span class="info-value">{ste.model_name}</span>
							</div>
						{/if}
						{#if ste.category_name}
							<div class="info-row">
								<span class="info-label">Категория</span>
								<span class="info-line"></span>
								<span class="info-value">{ste.category_name}</span>
							</div>
						{/if}
					</div>
				</div>
			</div>

			<!-- Характеристики -->
			{#if features.length > 0}
				<section class="features-section">
					<h2 class="section-title-large">Характеристики товара</h2>
					<div class="features-grid">
						{#each features as feature}
							<div class="feature-row">
								<span class="feature-label">{feature.name}</span>
								<span class="feature-line"></span>
								<span class="feature-value">{feature.value}</span>
							</div>
						{/each}
					</div>
				</section>
			{/if}
		{/if}
	</main>
</div>

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

	.loading,
	.error {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		min-height: 400px;
		gap: 16px;
	}

	.btn-primary {
		background: #cd1f15;
		color: white;
		padding: 10px 24px;
		border-radius: 4px;
		border: none;
		cursor: pointer;
		font-family: inherit;
		font-size: 14px;
	}

	.top-row {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 24px;
	}

	.breadcrumbs {
		display: flex;
		align-items: center;
		gap: 4px;
	}

	.breadcrumb-link {
		color: #333;
		font-size: 14px;
		text-decoration: none;
	}

	.breadcrumb-link:hover {
		text-decoration: underline;
	}

	.breadcrumb-current {
		color: #333;
		font-size: 14px;
	}

	.breadcrumb-separator {
		display: flex;
		align-items: center;
	}

	.ste-id-container {
		display: flex;
		align-items: center;
		gap: 4px;
	}

	.ste-id-text {
		color: #76767a;
		font-size: 14px;
	}

	.copy-btn {
		background: none;
		border: none;
		cursor: pointer;
		padding: 4px;
		display: flex;
		align-items: center;
		justify-content: center;
	}

	.copy-btn:hover {
		opacity: 0.7;
	}

	.card-main {
		display: flex;
		gap: 76px;
		margin-bottom: 40px;
		background: white;
		padding: 24px;
		border-radius: 12px;
	}

	.card-image-container {
		flex-shrink: 0;
		width: 280px;
		height: 336px;
		background: linear-gradient(0deg, rgba(0, 0, 0, 0.03), rgba(0, 0, 0, 0.03));
		border-radius: 12px;
		display: flex;
		align-items: center;
		justify-content: center;
		overflow: hidden;
	}

	.card-image {
		width: 100%;
		height: 100%;
		object-fit: cover;
	}

	.card-info {
		flex: 1;
		display: flex;
		flex-direction: column;
	}

	.card-title {
		font-size: 22px;
		font-weight: 600;
		line-height: 28px;
		color: #000;
		margin: 0 0 16px;
	}

	.section-title {
		font-size: 22px;
		font-weight: 500;
		line-height: 28px;
		color: #333;
		margin: 0 0 16px;
	}

	.section-title-large {
		font-size: 30px;
		font-weight: 500;
		line-height: 36px;
		color: #333;
		margin: 0 0 24px;
	}

	.info-table {
		display: flex;
		flex-direction: column;
		gap: 8px;
	}

	.info-row {
		display: flex;
		align-items: center;
		gap: 12px;
	}

	.info-label {
		color: #76767a;
		font-size: 16px;
		white-space: nowrap;
	}

	.info-line {
		flex: 1;
		height: 1px;
		background: #e5e5eb;
	}

	.info-value {
		color: #333;
		font-size: 16px;
		text-align: right;
	}

	.info-link {
		color: #0050b2;
		text-decoration: none;
	}

	.info-link:hover {
		text-decoration: underline;
	}

	.features-section {
		background: white;
		padding: 24px;
		border-radius: 12px;
	}

	.features-grid {
		display: grid;
		grid-template-columns: repeat(2, 1fr);
		gap: 16px 48px;
	}

	.feature-row {
		display: flex;
		align-items: center;
		gap: 12px;
	}

	.feature-label {
		color: #76767a;
		font-size: 16px;
		white-space: nowrap;
		overflow: hidden;
		text-overflow: ellipsis;
		max-width: 40%;
		flex-shrink: 0;
	}

	.feature-line {
		flex: 1;
		height: 1px;
		background: #e5e5eb;
		min-width: 20px;
	}

	.feature-value {
		color: #333;
		font-size: 16px;
		text-align: right;
		overflow: hidden;
		text-overflow: ellipsis;
		max-width: 50%;
		word-break: break-word;
	}

	@media (max-width: 1200px) {
		.content {
			padding: 24px 40px 40px;
		}

		.features-grid {
			grid-template-columns: 1fr;
		}
	}

	@media (max-width: 768px) {
		.content {
			padding: 16px;
		}

		.card-main {
			flex-direction: column;
			gap: 24px;
		}

		.card-image-container {
			width: 100%;
			height: 280px;
		}
	}
</style>
