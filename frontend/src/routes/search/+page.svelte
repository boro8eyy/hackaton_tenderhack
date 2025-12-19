<script lang="ts">
	import { goto } from '$app/navigation'
	import { page } from '$app/stores'
	import { getCategories, type Category } from '$lib/api/categories'
	import { search } from '$lib/api/search'
	import type { Ste } from '$lib/api/ste'
	import Checkbox from '$lib/components/Checkbox.svelte'
	import Header from '$lib/components/Header.svelte'
	import { onMount } from 'svelte'

	// Состояние поиска из URL
	let urlQuery = $derived($page.url.searchParams.get('query') ?? '')
	let urlExact = $derived($page.url.searchParams.get('exact') === 'true')
	let urlPage = $derived(
		parseInt($page.url.searchParams.get('page') ?? '1', 10)
	)
	let urlCategory = $derived(
		$page.url.searchParams.get('category')
			? parseInt($page.url.searchParams.get('category')!, 10)
			: null
	)

	// Локальное состояние формы
	let searchInput = $state('')
	let exactSearchInput = $state(false)

	// Состояние результатов
	let results = $state<Ste[]>([])
	let totalResults = $state(0)
	let totalPages = $state(1)
	let currentPage = $state(1)
	let perPage = $state(10)

	let isLoading = $state(false)
	let hasSearched = $state(false)
	let errorMessage = $state('')

	// Фильтры
	let categories = $state<Category[]>([])
	let selectedCategoryId = $state<number | null>(null)
	let sortBy = $state<'relevance' | 'name' | 'category'>('relevance')

	// Локальная сортировка результатов (серверная пагинация, клиентская сортировка)
	let sortedResults = $derived.by(() => {
		if (sortBy === 'name') {
			return [...results].sort((a, b) => a.name.localeCompare(b.name))
		} else if (sortBy === 'category') {
			return [...results].sort((a, b) =>
				(a.category_name ?? '').localeCompare(b.category_name ?? '')
			)
		}
		return results
	})

	onMount(async () => {
		// Загружаем категории для фильтра
		try {
			categories = await getCategories()
		} catch {
			console.error('Не удалось загрузить категории')
		}

		// Если есть query в URL, инициализируем состояние и выполняем поиск
		if (urlQuery) {
			searchInput = urlQuery
			exactSearchInput = urlExact
			currentPage = urlPage
			selectedCategoryId = urlCategory
			await performSearch()
		}
	})

	async function performSearch(resetPage = false) {
		if (!searchInput.trim()) {
			errorMessage = 'Введите поисковый запрос'
			return
		}

		if (resetPage) {
			currentPage = 1
		}

		isLoading = true
		errorMessage = ''
		hasSearched = true

		try {
			const response = await search({
				query: searchInput.trim(),
				exact: exactSearchInput,
				page: currentPage,
				per_page: perPage,
				category_id: selectedCategoryId,
			})

			results = response.items
			totalResults = response.total
			totalPages = response.total_pages
			currentPage = response.page
		} catch {
			errorMessage = 'Ошибка при выполнении поиска'
			results = []
			totalResults = 0
			totalPages = 1
		} finally {
			isLoading = false
		}
	}

	function updateUrl() {
		const params = new URLSearchParams()
		if (searchInput.trim()) params.set('query', searchInput.trim())
		if (exactSearchInput) params.set('exact', 'true')
		if (currentPage > 1) params.set('page', currentPage.toString())
		if (selectedCategoryId !== null)
			params.set('category', selectedCategoryId.toString())
		goto(`/search?${params.toString()}`, { replaceState: true })
	}

	function handleSearchKeydown(event: KeyboardEvent) {
		if (event.key === 'Enter') {
			handleSearch()
		}
	}

	function handleSearch() {
		currentPage = 1
		updateUrl()
		performSearch(true)
	}

	function handleCategoryChange() {
		currentPage = 1
		updateUrl()
		performSearch(true)
	}

	function clearFilters() {
		selectedCategoryId = null
		sortBy = 'relevance'
		currentPage = 1
		updateUrl()
		performSearch(true)
	}

	function goToPage(page: number) {
		if (page >= 1 && page <= totalPages && page !== currentPage) {
			currentPage = page
			updateUrl()
			performSearch()
			// Прокрутка к началу результатов
			document
				.querySelector('.results-header')
				?.scrollIntoView({ behavior: 'smooth' })
		}
	}

	function goToResult(item: Ste) {
		const cardId = item.card_id ?? 0
		goto(`/card/${cardId}/${item.id}`)
	}

	// Вычисляем диапазон показанных результатов
	let showingFrom = $derived((currentPage - 1) * perPage + 1)
	let showingTo = $derived(Math.min(currentPage * perPage, totalResults))
</script>

<svelte:head>
	<title>{urlQuery ? `${urlQuery} — Поиск` : 'Поиск'} | TenderHack</title>
</svelte:head>

<div class="page-wrapper">
	<Header />

	<main class="content">
		<h1 class="page-title">Поиск</h1>

		<!-- Поисковая строка -->
		<div class="search-section">
			<div class="search-input-group">
				<input
					type="text"
					placeholder="Введите поисковый запрос"
					class="search-input"
					bind:value={searchInput}
					onkeydown={handleSearchKeydown}
				/>
				<button
					class="search-submit-btn"
					onclick={handleSearch}
					disabled={isLoading}
					aria-label="Поиск"
				>
					{#if isLoading}
						<svg class="spinner" width="20" height="20" viewBox="0 0 24 24">
							<circle
								cx="12"
								cy="12"
								r="10"
								stroke="white"
								stroke-width="2"
								fill="none"
								stroke-dasharray="30 70"
							/>
						</svg>
					{:else}
						<svg width="20" height="20" viewBox="0 0 24 24" fill="none">
							<circle cx="11" cy="11" r="7" stroke="white" stroke-width="2" />
							<path
								d="M16 16L21 21"
								stroke="white"
								stroke-width="2"
								stroke-linecap="round"
							/>
						</svg>
					{/if}
				</button>
			</div>

			<label class="checkbox-container">
				<Checkbox
					checked={exactSearchInput}
					onchange={v => (exactSearchInput = v)}
				/>
				<span class="checkbox-text">Точный поиск</span>
			</label>
		</div>

		{#if errorMessage}
			<div class="error-message">{errorMessage}</div>
		{/if}

		{#if hasSearched}
			<!-- Статистика и фильтры -->
			<div class="results-header">
				<div class="results-stats">
					<span class="stats-total">Найдено: {totalResults} товаров</span>
				</div>

				<div class="filters">
					<div class="filter-group">
						<label class="filter-label" for="category-filter">Категория</label>
						<select
							id="category-filter"
							class="filter-select"
							bind:value={selectedCategoryId}
							onchange={handleCategoryChange}
						>
							<option value={null}>Все категории</option>
							{#each categories as category}
								<option value={category.id}>{category.name}</option>
							{/each}
						</select>
					</div>

					<div class="filter-group">
						<label class="filter-label" for="sort-filter">Сортировка</label>
						<select id="sort-filter" class="filter-select" bind:value={sortBy}>
							<option value="relevance">По релевантности</option>
							<option value="name">По названию</option>
							<option value="category">По категории</option>
						</select>
					</div>

					<button class="clear-filters-btn" onclick={clearFilters}>
						Сбросить фильтры
					</button>
				</div>
			</div>

			<!-- Результаты поиска -->
			{#if isLoading}
				<div class="loading">
					<div class="loading-spinner"></div>
					<span>Поиск...</span>
				</div>
			{:else if sortedResults.length === 0}
				<div class="no-results">
					<svg
						width="64"
						height="64"
						viewBox="0 0 24 24"
						fill="none"
						stroke="#999"
						stroke-width="1.5"
					>
						<circle cx="11" cy="11" r="8" />
						<path d="M21 21l-4.35-4.35" stroke-linecap="round" />
						<path d="M8 11h6" stroke-linecap="round" />
					</svg>
					<p class="no-results-text">По вашему запросу ничего не найдено</p>
					<p class="no-results-hint">
						Попробуйте изменить запрос или сбросить фильтры
					</p>
				</div>
			{:else}
				<div class="results-grid">
					{#each sortedResults as item}
						<button
							class="result-card"
							onclick={() => goToResult(item)}
							type="button"
						>
							<div class="result-image">
								{#if item.image_url}
									<img src={item.image_url} alt={item.name} />
								{:else}
									<div class="image-placeholder">
										<svg
											width="40"
											height="40"
											viewBox="0 0 24 24"
											fill="none"
											stroke="#999"
										>
											<rect
												x="3"
												y="3"
												width="18"
												height="18"
												rx="2"
												stroke-width="1.5"
											/>
											<circle cx="8.5" cy="8.5" r="1.5" fill="#999" />
											<path
												d="M21 15l-5-5L5 21"
												stroke-width="1.5"
												stroke-linecap="round"
											/>
										</svg>
									</div>
								{/if}
							</div>

							<div class="result-content">
								<h3 class="result-name">{item.name}</h3>

								{#if item.category_name}
									<div class="result-category">{item.category_name}</div>
								{/if}

								<div class="result-details">
									{#if item.manufacturer}
										<span class="detail-item">
											<span class="detail-label">Производитель:</span>
											<span class="detail-value">{item.manufacturer}</span>
										</span>
									{/if}
									{#if item.model_name}
										<span class="detail-item">
											<span class="detail-label">Модель:</span>
											<span class="detail-value">{item.model_name}</span>
										</span>
									{/if}
									{#if item.country_of_origin}
										<span class="detail-item">
											<span class="detail-label">Страна:</span>
											<span class="detail-value">{item.country_of_origin}</span>
										</span>
									{/if}
								</div>
							</div>
							<div class="result-arrow">
								<svg
									width="20"
									height="20"
									viewBox="0 0 24 24"
									fill="none"
									stroke="currentColor"
									stroke-width="2"
								>
									<path
										d="M9 18l6-6-6-6"
										stroke-linecap="round"
										stroke-linejoin="round"
									/>
								</svg>
							</div>
						</button>
					{/each}
				</div>

				<!-- Пагинация -->
				{#if totalPages > 1}
					<div class="pagination">
						<button
							class="pagination-btn pagination-prev"
							disabled={currentPage === 1}
							onclick={() => goToPage(currentPage - 1)}
						>
							<svg
								width="16"
								height="16"
								viewBox="0 0 24 24"
								fill="none"
								stroke="currentColor"
								stroke-width="2"
							>
								<path
									d="M15 18l-6-6 6-6"
									stroke-linecap="round"
									stroke-linejoin="round"
								/>
							</svg>
							<span>Назад</span>
						</button>

						<div class="pagination-pages">
							{#if currentPage > 2}
								<button class="pagination-page" onclick={() => goToPage(1)}
									>1</button
								>
								{#if currentPage > 3}
									<span class="pagination-ellipsis">...</span>
								{/if}
							{/if}

							{#each Array.from({ length: totalPages }, (_, i) => i + 1) as page}
								{#if page >= currentPage - 1 && page <= currentPage + 1}
									<button
										class="pagination-page"
										class:active={page === currentPage}
										onclick={() => goToPage(page)}
									>
										{page}
									</button>
								{/if}
							{/each}

							{#if currentPage < totalPages - 1}
								{#if currentPage < totalPages - 2}
									<span class="pagination-ellipsis">...</span>
								{/if}
								<button
									class="pagination-page"
									onclick={() => goToPage(totalPages)}>{totalPages}</button
								>
							{/if}
						</div>

						<button
							class="pagination-btn pagination-next"
							disabled={currentPage === totalPages}
							onclick={() => goToPage(currentPage + 1)}
						>
							<span>Вперёд</span>
							<svg
								width="16"
								height="16"
								viewBox="0 0 24 24"
								fill="none"
								stroke="currentColor"
								stroke-width="2"
							>
								<path
									d="M9 18l6-6-6-6"
									stroke-linecap="round"
									stroke-linejoin="round"
								/>
							</svg>
						</button>
					</div>

					<div class="pagination-info">
						Показано {showingFrom}–{showingTo} из {totalResults}
					</div>
				{/if}
			{/if}
		{/if}
	</main>
</div>

<style>
	:global(body) {
		margin: 0;
		font-family: 'Golos Text', sans-serif;
	}

	.page-wrapper {
		background-color: #f2f2f2;
		min-height: 100vh;
	}

	.content {
		padding: 40px 160px;
		max-width: 1400px;
		margin: 0 auto;
	}

	.page-title {
		font-size: 32px;
		font-weight: 600;
		margin: 0 0 24px 0;
		color: #333;
	}

	/* Поисковая секция */
	.search-section {
		background: white;
		padding: 24px;
		border-radius: 8px;
		margin-bottom: 24px;
	}

	.search-input-group {
		display: flex;
		border: 1px solid #ccc;
		height: 48px;
		border-radius: 8px;
		overflow: hidden;
		margin-bottom: 12px;
	}

	.search-input {
		flex: 1;
		border: none;
		padding: 0 16px;
		outline: none;
		font-family: inherit;
		font-size: 16px;
	}

	.search-input::placeholder {
		color: #999;
	}

	.search-submit-btn {
		background: #cd1f15;
		width: 56px;
		display: flex;
		justify-content: center;
		align-items: center;
		border: none;
		cursor: pointer;
		transition: background 0.2s;
	}

	.search-submit-btn:hover:not(:disabled) {
		background: #b31a12;
	}

	.search-submit-btn:disabled {
		opacity: 0.7;
		cursor: not-allowed;
	}

	.spinner {
		animation: spin 1s linear infinite;
	}

	@keyframes spin {
		from {
			transform: rotate(0deg);
		}
		to {
			transform: rotate(360deg);
		}
	}

	.checkbox-container {
		display: flex;
		gap: 8px;
		font-size: 14px;
		align-items: center;
		cursor: pointer;
	}

	.checkbox-text {
		line-height: 1;
		color: #333;
	}

	/* Ошибка */
	.error-message {
		background: #fee2e2;
		border: 1px solid #fecaca;
		color: #dc2626;
		padding: 12px 16px;
		border-radius: 8px;
		margin-bottom: 24px;
		font-size: 14px;
	}

	/* Заголовок результатов */
	.results-header {
		background: white;
		padding: 20px 24px;
		border-radius: 8px;
		margin-bottom: 24px;
	}

	.results-stats {
		margin-bottom: 16px;
	}

	.stats-total {
		font-size: 18px;
		font-weight: 600;
		color: #333;
	}

	.filters {
		display: flex;
		flex-wrap: wrap;
		gap: 16px;
		align-items: flex-end;
	}

	.filter-group {
		display: flex;
		flex-direction: column;
		gap: 4px;
	}

	.filter-label {
		font-size: 12px;
		color: #666;
	}

	.filter-select {
		padding: 8px 12px;
		border: 1px solid #ccc;
		border-radius: 4px;
		font-family: inherit;
		font-size: 14px;
		min-width: 150px;
		background: white;
		cursor: pointer;
	}

	.clear-filters-btn {
		background: none;
		border: 1px solid #ccc;
		padding: 8px 16px;
		border-radius: 4px;
		font-family: inherit;
		font-size: 14px;
		color: #666;
		cursor: pointer;
		transition: all 0.2s;
	}

	.clear-filters-btn:hover {
		border-color: #999;
		color: #333;
	}

	/* Загрузка */
	.loading {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		padding: 60px;
		color: #666;
		gap: 16px;
	}

	.loading-spinner {
		width: 40px;
		height: 40px;
		border: 3px solid #f3f3f3;
		border-top: 3px solid #cd1f15;
		border-radius: 50%;
		animation: spin 1s linear infinite;
	}

	/* Нет результатов */
	.no-results {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		padding: 60px;
		background: white;
		border-radius: 8px;
		text-align: center;
	}

	.no-results-text {
		font-size: 18px;
		color: #333;
		margin: 16px 0 8px;
	}

	.no-results-hint {
		font-size: 14px;
		color: #666;
		margin: 0;
	}

	/* Результаты */
	.results-grid {
		display: flex;
		flex-direction: column;
		gap: 12px;
	}

	.result-card {
		display: flex;
		align-items: center;
		background: white;
		border-radius: 8px;
		padding: 16px;
		gap: 16px;
		border: none;
		cursor: pointer;
		text-align: left;
		font-family: inherit;
		transition:
			box-shadow 0.2s,
			transform 0.2s;
		width: 100%;
	}

	.result-card:hover {
		box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
		transform: translateY(-2px);
	}

	.result-image {
		width: 80px;
		height: 80px;
		flex-shrink: 0;
		border-radius: 8px;
		overflow: hidden;
		background: #f5f5f5;
	}

	.result-image img {
		width: 100%;
		height: 100%;
		object-fit: cover;
	}

	.image-placeholder {
		width: 100%;
		height: 100%;
		display: flex;
		align-items: center;
		justify-content: center;
	}

	.result-content {
		flex: 1;
		min-width: 0;
	}

	.result-name {
		font-size: 16px;
		font-weight: 600;
		color: #333;
		margin: 0 0 4px;
		white-space: nowrap;
		overflow: hidden;
		text-overflow: ellipsis;
	}

	.result-category {
		font-size: 13px;
		color: #666;
		margin-bottom: 8px;
	}

	.result-details {
		display: flex;
		flex-wrap: wrap;
		gap: 12px;
	}

	.detail-item {
		font-size: 12px;
	}

	.detail-label {
		color: #999;
	}

	.detail-value {
		color: #333;
		margin-left: 4px;
	}

	.result-arrow {
		color: #999;
		transition:
			color 0.2s,
			transform 0.2s;
	}

	.result-card:hover .result-arrow {
		color: #cd1f15;
		transform: translateX(4px);
	}

	/* Пагинация */
	.pagination {
		display: flex;
		align-items: center;
		justify-content: center;
		gap: 8px;
		margin-top: 24px;
		padding: 16px;
		background: white;
		border-radius: 8px;
	}

	.pagination-btn {
		display: flex;
		align-items: center;
		gap: 6px;
		padding: 8px 16px;
		background: white;
		border: 1px solid #ccc;
		border-radius: 4px;
		font-family: inherit;
		font-size: 14px;
		color: #333;
		cursor: pointer;
		transition: all 0.2s;
	}

	.pagination-btn:hover:not(:disabled) {
		border-color: #cd1f15;
		color: #cd1f15;
	}

	.pagination-btn:disabled {
		opacity: 0.5;
		cursor: not-allowed;
	}

	.pagination-pages {
		display: flex;
		align-items: center;
		gap: 4px;
	}

	.pagination-page {
		min-width: 36px;
		height: 36px;
		padding: 0 8px;
		background: white;
		border: 1px solid #ccc;
		border-radius: 4px;
		font-family: inherit;
		font-size: 14px;
		color: #333;
		cursor: pointer;
		transition: all 0.2s;
	}

	.pagination-page:hover {
		border-color: #cd1f15;
		color: #cd1f15;
	}

	.pagination-page.active {
		background: #cd1f15;
		border-color: #cd1f15;
		color: white;
	}

	.pagination-ellipsis {
		padding: 0 8px;
		color: #666;
	}

	.pagination-info {
		text-align: center;
		font-size: 13px;
		color: #666;
		margin-top: 12px;
	}

	/* Адаптив */
	@media (max-width: 1200px) {
		.content {
			padding: 40px;
		}
	}

	@media (max-width: 768px) {
		.content {
			padding: 20px 16px;
		}

		.page-title {
			font-size: 24px;
		}

		.filters {
			flex-direction: column;
			align-items: stretch;
		}

		.filter-select {
			width: 100%;
		}

		.result-card {
			flex-direction: column;
			align-items: flex-start;
		}

		.result-image {
			width: 100%;
			height: 150px;
		}

		.result-arrow {
			display: none;
		}
	}
</style>
